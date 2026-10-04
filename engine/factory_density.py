"""Regional peer counts from reviewed MOEA factory survey snapshots.

Factory counts are not company counts, vacancy counts or workers competing
for the same jobs. No synthetic fallback is allowed.
"""
import csv
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / 'data' / 'raw' / 'factory_counts.csv'
SOURCE = 'https://service.moea.gov.tw/EE520/investigate/InvestigateG.aspx'
FIELDS = {'年度', '行政區', '行業中類代碼', '行業名稱', '營運中工廠家數', '資料來源'}

def get_regional_peer_density(district='大雅區', year=113, industry_code=None):
    """Return observed factory counts for an exact district/year/category.

    None selects only available categories, never implies a district total.
    Historical snapshots must be supplied explicitly; no live refresh occurs.
    """
    year = int(year)
    code = str(industry_code).zfill(2) if industry_code is not None else None
    rows = []
    if SNAPSHOT.exists():
        with SNAPSHOT.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if not FIELDS.issubset(reader.fieldnames or []):
                raise ValueError('Factory snapshot is missing required columns')
            seen = set()
            for raw in reader:
                key = (int(raw['年度']), raw['行政區'], raw['行業中類代碼'].zfill(2))
                if key in seen:
                    raise ValueError('Duplicate factory district/year/industry record')
                seen.add(key)
                if key[:2] != (year, district) or (code is not None and key[2] != code):
                    continue
                value = raw['營運中工廠家數'].strip()
                count = int(value.replace(',', '')) if value not in {'*', '-', ''} else None
                if count is not None and count < 0:
                    raise ValueError('Negative factory count')
                rows.append({'year': year, 'district': district, 'industry_code': key[2],
                             'industry_name': raw['行業名稱'], 'factory_count': count,
                             'value_status': 'observed' if count is not None else 'unavailable',
                             'source_url': raw['資料來源']})
    known = [r['factory_count'] for r in rows if r['factory_count'] is not None]
    count = sum(known) if rows and len(known) == len(rows) else None
    status = 'available' if count is not None else ('unavailable' if rows else 'no_data')
    evidence = {'indicator_name': '區域同類營運中工廠家數',
                'official_sources': ['經濟部工廠校正及營運調查'], 'source_url': SOURCE,
                'source_tables': ['factory_counts.csv'], 'data_period': f'{year}年',
                'geography': f'臺中市{district}', 'data_mode': 'reviewed_official_snapshot',
                'verification_status': 'SOURCE_CHECKED' if status == 'available' else 'NO_DATA',
                'calculation_steps': ['依年度、行政區與行業中類篩選官方調查值；無資料不補零。'],
                'limitations': ['只涵蓋已匯入的行業，不代表全區工廠總數。',
                                '工廠家數不等於公司家數、徵才需求或缺工人數。',
                                '未提供面積或通勤資料，不計算每平方公里密度。',
                                '普查年可能缺資料；*與-保留為未知值。']}
    return {'status': status, 'district': district, 'year': year, 'industry_code': code,
            'factory_count': count, 'unit': '家', 'coverage': 'imported_categories_only',
            'industries': rows, 'evidence': evidence}
