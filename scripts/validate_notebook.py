"""Validação estática local; não substitui o teste de integração no AIDP."""
import ast
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'notebooks/Access_ALH_Data_dev.ipynb'
notebook = json.loads(path.read_text())
assert notebook['nbformat'] == 4
count = 0
for index, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        ast.parse(''.join(cell['source']), filename=f'{path.name}:cell-{index}')
        assert cell['outputs'] == [], 'Remova outputs antes de versionar'
        assert cell['execution_count'] is None
        count += 1
assert count > 0
print(f'OK: JSON e sintaxe de {count} células Python; nenhum output persistido.')
