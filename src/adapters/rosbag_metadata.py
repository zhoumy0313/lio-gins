"""Read-only unencrypted ROS bag v2 metadata and bounded raw samples.

Format checked against ROS ros_comm/noetic-devel tools/rosbag/src/rosbag/bag.py.
This is a narrow interface auditor, not a ROS deserializer/replay replacement.
"""
import struct
import io
import bz2
from collections import Counter


def read_exact(f,n):
    data=f.read(n)
    if len(data)!=n:raise ValueError('truncated bag record')
    return data


def fields(data):
    result={};i=0
    while i<len(data):
        n=struct.unpack_from('<I',data,i)[0];i+=4
        if n==0 or i+n>len(data):raise ValueError('invalid bag header field')
        key,value=data[i:i+n].split(b'=',1);i+=n
        if key.decode() in result:raise ValueError('duplicate bag header field')
        result[key.decode()]=value
    return result


def uint(h,k):
    return int.from_bytes(h[k],'little')


def stamp(raw):
    sec,nsec=struct.unpack('<II',raw)
    if nsec>=1000000000:raise ValueError('invalid nanosecond field')
    return sec+nsec*1e-9


def header(f):
    size=struct.unpack('<I',read_exact(f,4))[0]
    if size>1024*1024:raise ValueError('unexpected bag header size')
    h=fields(read_exact(f,size));n=struct.unpack('<I',read_exact(f,4))[0]
    return h,n


def read_metadata(path):
    with open(path,'rb') as f:
        if read_exact(f,13)!=b'#ROSBAG V2.0\n':raise ValueError('not ROS bag v2')
        h,n=header(f)
        if uint(h,'op')!=3:raise ValueError('missing file header')
        index=uint(h,'index_pos');connections={};chunks=[];counts=Counter()
        f.seek(index)
        for _ in range(uint(h,'conn_count')):
            c,n=header(f)
            if uint(c,'op')!=7:raise ValueError('expected connection record')
            d=fields(read_exact(f,n));connections[uint(c,'conn')]={'topic':c['topic'].decode(),'type':d['type'].decode(),'md5sum':d['md5sum'].decode()}
        for _ in range(uint(h,'chunk_count')):
            c,n=header(f)
            if uint(c,'op')!=6 or uint(c,'ver')!=1 or n!=uint(c,'count')*8:raise ValueError('invalid chunk info')
            d=read_exact(f,n);cc={}
            for cid,num in struct.iter_unpack('<II',d):cc[cid]=num;counts[cid]+=num
            chunks.append({'position':uint(c,'chunk_pos'),'start':stamp(c['start_time']),'end':stamp(c['end_time']),'counts':cc})
        if f.read(1):raise ValueError('unexpected trailing index data')
        if set(counts)-set(connections):raise ValueError('unknown indexed connection')
        for cid,c in connections.items():c['count']=counts[cid]
        return {'index_position':index,'connection_count':len(connections),'chunk_count':len(chunks),'start_unix':min(c['start'] for c in chunks),'end_unix':max(c['end'] for c in chunks),'connections':connections,'chunks':chunks}


def bounded_samples(path,meta,limits):
    """First N serialized samples per requested topic, in bag record order."""
    results={topic:[] for topic in limits}
    with open(path,'rb') as f:
        for chunk in meta['chunks']:
            if all(len(results[t])>=limits[t] for t in limits):break
            relevant=[cid for cid in chunk['counts'] if meta['connections'][cid]['topic'] in limits and len(results[meta['connections'][cid]['topic']])<limits[meta['connections'][cid]['topic']]]
            if not relevant:continue
            f.seek(chunk['position']);h,n=header(f)
            if uint(h,'op')!=5:raise ValueError('expected chunk')
            compressed=read_exact(f,n)
            if h['compression']==b'none':data=compressed
            elif h['compression']==b'bz2':data=bz2.decompress(compressed)
            elif h['compression']==b'lz4':
                import lz4.frame
                data=lz4.frame.decompress(compressed)
            else:raise ValueError('unsupported bag compression')
            if len(data)!=uint(h,'size'):raise ValueError('decompressed chunk size mismatch')
            block=io.BytesIO(data);end=len(data)
            while block.tell()<end:
                c,size=header(block);op=uint(c,'op')
                if op==2 and uint(c,'conn') in relevant:
                    topic=meta['connections'][uint(c,'conn')]['topic']
                    if len(results[topic])<limits[topic]:results[topic].append((stamp(c['time']),read_exact(block,size)))
                    else:block.seek(size,1)
                else:block.seek(size,1)
            if block.tell()!=end:raise ValueError('chunk record boundary mismatch')
    if any(len(results[t])<limits[t] for t in limits):raise ValueError('insufficient bounded samples')
    return results


def message_header(data):
    seq,sec,ns,n=struct.unpack_from('<IIII',data)
    return {'seq':seq,'stamp':stamp(struct.pack('<II',sec,ns)),'frame_id':data[16:16+n].decode()},16+n


def decode_imu(data):
    h,i=message_header(data)
    orientation=struct.unpack_from('<4d',data,i);i+=13*8
    angular=struct.unpack_from('<3d',data,i);i+=12*8
    linear=struct.unpack_from('<3d',data,i)
    return {**h,'orientation_xyzw':orientation,'angular_velocity':angular,'linear_acceleration':linear}


def decode_insprobe_imu(data):
    h,i=message_header(data)
    week,sow=struct.unpack_from('<Hd',data,i);i+=10
    a=struct.unpack_from('<12d',data,i)
    return {**h,'week':week,'sow':sow,'angular_velocity':a[:3],'linear_acceleration':a[3:6],'incremental_angles':a[6:9],'incremental_velocity':a[9:12]}


def decode_pointcloud_layout(data):
    h,i=message_header(data);height,width,count=struct.unpack_from('<III',data,i);i+=12;fs=[]
    for _ in range(count):
        n=struct.unpack_from('<I',data,i)[0];i+=4;name=data[i:i+n].decode();i+=n
        offset,dtype,num=struct.unpack_from('<IBI',data,i);i+=9
        fs.append({'name':name,'offset':offset,'datatype':dtype,'count':num})
    big,step,rowstep,n=struct.unpack_from('<BIII',data,i);i+=13
    if big or n!=height*rowstep:raise ValueError('unexpected endian/cloud data length')
    ts=next(x for x in fs if x['name']=='timestamp')
    if ts['datatype']!=8:raise ValueError('AT128 timestamp must be float64')
    times=[struct.unpack_from('<d',data,i+k*step+ts['offset'])[0] for k in range(width)]
    return {**h,'height':height,'width':width,'fields':fs,'point_step':step,'first_point_time':times[0],'last_point_time':times[-1],'min_point_time':min(times),'max_point_time':max(times),'point_time_backward_count':sum(b<a for a,b in zip(times,times[1:]))}
