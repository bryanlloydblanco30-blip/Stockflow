# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
ROOT = Path.cwd()

datas = [
    (str(ROOT / "frontend" / "dist"), "frontend/dist"),
    (str(ROOT / "data"), "data"),
    (str(ROOT / "stockflow.db"), "."),
]

hidden_imports = [
    "sqlite3",
    "mimetypes",
    "urllib.parse",
    "http.server",
    "backend",
    "backend.api_server",
    "backend.db",
    "backend.db.schema",
    "backend.db.connection",
    "backend.db.storage",
    "backend.db.backup",
    "backend.models",
    "backend.models.category",
    "backend.models.product",
    "backend.models.batch",
    "backend.models.transaction",
    "backend.models.transaction_line",
    "backend.models.settings",
    "backend.models.location",
    "backend.ds",
    "backend.ds.bst",
    "backend.ds.trie",
    "backend.ds.min_heap",
    "backend.ds.max_heap",
    "backend.ds.linked_list",
    "backend.ds.stack",
    "backend.ds.prefix_sums",
    "backend.ds.size_k_heap",
    "backend.services",
    "backend.services.alert_service",
    "backend.services.category_service",
    "backend.services.fefo_service",
    "backend.services.inventory_service",
    "backend.services.pos_service",
    "backend.services.product_service",
    "backend.services.report_service",
    "backend.services.restock_service",
    "backend.services.undo_service",
]

a = Analysis(
    ['desktop_app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['flet', 'tkinter', 'matplotlib', 'scipy', 'numpy', 'test', 'tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StockFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "frontend" / "public" / "favicon.png") if (ROOT / "frontend" / "public" / "favicon.png").is_file() else None,
)
