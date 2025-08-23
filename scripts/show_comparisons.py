import sys
from pathlib import Path

# ensure project root is on sys.path so local packages (services, utils) import correctly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.competitor_analysis import CompetitorAnalyzer

an = CompetitorAnalyzer()

pairs = [
    ("Samsung", "Lenovo", "Laptops"),
    ("Apple", "Samsung", "Mobiles"),
]

for a, b, domain in pairs:
    res = an._get_basic_analysis(a, b, domain)
    print(f"\n--- {a} vs {b} ({domain}) ---")
    ms = res['market_analysis']['market_share']
    print('Market Share:')
    for k, v in ms.items():
        print(' ', k, ':', v)
    print('Revenue labels:', res['market_analysis']['revenue_trends']['labels'])
    for ds in res['market_analysis']['revenue_trends']['datasets']:
        print('  ', ds['label'], ds['data'])
