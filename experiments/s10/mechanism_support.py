"""Scope only the already registered diagnostic windows, preserving tail gaps."""
def event_window_updates(rows, events, pre_s=40, post_s=180):
    return [u for u in rows if any(e['recovery_start_sow']-pre_s <= u['measurement_sow'] < e['recovery_start_sow']+post_s for e in events)]
