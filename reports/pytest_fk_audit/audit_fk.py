import uuid
from pathlib import Path

import config as _cfg

root = Path(__file__).resolve().parent
dbp = (root / f"c_{uuid.uuid4().hex[:8]}.db").resolve()
_cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(dbp).replace("\\", "/")

from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    insp = inspect(db.engine)
    print("ALL TABLES:", sorted(insp.get_table_names()))
    for t in sorted(insp.get_table_names()):
        for fk in insp.get_foreign_keys(t):
            ref = fk.get("referred_table")
            if ref in ("users", "classes", "class_students"):
                print(
                    "FK",
                    t,
                    fk.get("constrained_columns"),
                    "->",
                    ref,
                    fk.get("referred_columns"),
                )
    mapping = {}
    for mapper in db.Model.registry.mappers:
        cls = mapper.class_
        if hasattr(cls, "__tablename__"):
            mapping[cls.__tablename__] = cls.__name__
    print("MODELS:")
    for k in sorted(mapping):
        print(" ", k, mapping[k])
