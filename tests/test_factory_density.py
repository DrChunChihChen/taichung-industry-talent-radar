import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import factory_density
from agent.explanation_gen import generate_explanation

class FactoryCountsTest(unittest.TestCase):
    def test_official_years(self):
        for year, count in [(111,207),(112,211),(113,219)]:
            result=factory_density.get_regional_peer_density('大雅區',year,'29')
            self.assertEqual(result['factory_count'],count)
            self.assertEqual(result['status'],'available')
    def test_no_synthetic_fallback(self):
        for district,year,code in [('潭子區',113,'29'),('大雅區',110,'29'),('大雅區',113,'25')]:
            result=factory_density.get_regional_peer_density(district,year,code)
            self.assertEqual(result['status'],'no_data')
            self.assertIsNone(result['factory_count'])
            answer=generate_explanation('DISTRICT_QUERY',{'data':result})
            self.assertIn('尚未匯入',answer)
    def test_suppressed_value_and_duplicates(self):
        header='年度,行政區,行業中類代碼,行業名稱,營運中工廠家數,資料來源\n'
        row='113,大雅區,29,機械設備業,*,https://example.com\n'
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'snapshot.csv';path.write_text(header+row,encoding='utf-8')
            with patch.object(factory_density,'SNAPSHOT',path):
                result=factory_density.get_regional_peer_density()
                self.assertIsNone(result['factory_count'])
                self.assertEqual(result['status'],'unavailable')
                path.write_text(header+row+row,encoding='utf-8')
                with self.assertRaises(ValueError):factory_density.get_regional_peer_density()
    def test_partial_coverage_not_city_total(self):
        result=factory_density.get_regional_peer_density()
        self.assertEqual(result['coverage'],'imported_categories_only')
        answer=generate_explanation('DISTRICT_QUERY',{'data':result})
        self.assertIn('219',answer)
        self.assertNotIn('新設公司總數',answer)

if __name__=='__main__':unittest.main()
