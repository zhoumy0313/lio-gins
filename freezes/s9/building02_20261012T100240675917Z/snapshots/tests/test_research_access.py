"""No accidental route or environment override may open heldout performance."""
import os,unittest
from unittest.mock import patch
from src.adapters.research_access import verify_access

class ResearchAccess(unittest.TestCase):
    def test_development_is_available_but_heldout_requires_actual_freeze(self):
        self.assertIsNone(verify_access('building00','development'))
        for sequence,role in [('parking00','heldout'),('parking00','development'),('building00','heldout'),('unknown','development')]:
            with self.assertRaises(ValueError):verify_access(sequence,role)

    def test_environment_does_not_bypass_guard(self):
        with patch.dict(os.environ,{'LIO_GINS_ALLOW_HELDOUT':'1','FREEZE_APPROVED':'true'}):
            with self.assertRaises(ValueError):verify_access('parking00','heldout')
