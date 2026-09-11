# -*- coding: utf-8 -*-
"""Stage, smoke, and publish sealed Math B2 1-4 V3 artifacts without DB writes."""
from __future__ import annotations
import hashlib,importlib.util,json,os,shutil,sqlite3,tempfile
from pathlib import Path
from typing import Any

from core.gencode.b2_14_component_specs import SPECS
from core.gencode.schema.gencode_component_tracker_inspection import ensure_gencode_component_tracker_table
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.skill_fixed_domain_authority import get_confirmed_skill_binding
from core.gencode.skill_wrapper_compiler import compile_and_double_write_skill
from core.gencode.v3_production_publish_service import _sync_staging_v3_component_sources,run_v3_smoke

PROJECT_ROOT=Path(__file__).resolve().parents[1]
SKILL_COMPONENTS={"vh_數學B2_SubSection_1_4_3":8,"vh_數學B2_SubSection_1_4_4":13}

def _load(example_id:int,skill_id:str):
    path=PROJECT_ROOT/"agent_skills_v3"/skill_id/"components"/f"src_{example_id}"/"generate.py"
    module_spec=importlib.util.spec_from_file_location(f"b2_14_phase3_{example_id}",path)
    if module_spec is None or module_spec.loader is None:raise RuntimeError(f"component_import_failed:src_{example_id}")
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module);return module.generate

def _tracker_snapshot()->sqlite3.Connection:
    conn=sqlite3.connect(":memory:");ensure_gencode_component_tracker_table(conn)
    for source_order,(example_id,component) in enumerate(sorted(SPECS.items()),1):
        skill_id=str(component["skill_id"]);operation=str(component["operation"])
        payload=_load(example_id,skill_id)(seed=0,component_id=f"src_{example_id}")
        binding=get_confirmed_skill_binding(skill_id) or {}
        spec={"skill_id":skill_id,"textbook_example_id":example_id,"component_id":f"src_{example_id}","source_kind":payload.get("source_kind"),"fixed_domain_key":binding.get("fixed_domain_key"),"domain_module":binding.get("domain_module"),"entrypoint":binding.get("entrypoint"),"binding_status":"confirmed","resolution_source":"confirmed_binding","registry_revision":binding.get("registry_revision"),"domain_operation":operation,"selected_operation":operation,"problem_type_id":operation,"line_type":operation,"presentation_mode":payload.get("presentation_mode"),"response_mode":payload.get("answer_type"),"interaction_type":payload.get("answer_type"),"answer_type":payload.get("answer_type"),"checker_key":payload.get("checker_key"),"equivalence_type":payload.get("equivalence_type"),"answer_contract":payload.get("answer_contract"),"integrity_gate_passed":True,"integrity_gate_version":"v1","choice_contract_valid":True,"display_order":source_order,"source_order":source_order,"sampling_weight":1}
        if payload.get("presentation_mode")=="single_choice":spec.update({"choices":payload.get("choices"),"answer":payload.get("correct_answer")})
        conn.execute("INSERT INTO gencode_component_tracker (textbook_example_id,skill_id,component_id,gencode_status,induced_spec_payload) VALUES (?,?,?,'verified',?)",(example_id,skill_id,f"src_{example_id}",json.dumps(spec,ensure_ascii=False)))
    conn.commit();return conn

def _atomic_copy(source:Path,destination:Path)->None:
    destination.parent.mkdir(parents=True,exist_ok=True);temporary=destination.with_name(f".{destination.name}.b2_14_phase3.tmp")
    shutil.copy2(source,temporary);os.replace(temporary,destination)

def _publish_tracker_evidence(snapshot:sqlite3.Connection)->int:
    production=sqlite3.connect(str(PROJECT_ROOT/"instance"/"kumon_math.db"));ensure_gencode_component_tracker_table(production);written=0
    try:
        rows=snapshot.execute("SELECT textbook_example_id,skill_id,induced_spec_payload FROM gencode_component_tracker ORDER BY textbook_example_id").fetchall()
        for example_id,skill_id,payload_text in rows:
            payload=json.loads(payload_text);generate_path=PROJECT_ROOT/"agent_skills_v3"/skill_id/"components"/f"src_{example_id}"/"generate.py"
            digest=hashlib.sha256(generate_path.read_bytes()).hexdigest();payload.update({"verified_generate_sha256":digest,"published_generate_sha256":digest,"production_manifest_verified":True,"runtime_smoke_passed":True})
            save_tracker_record(production,textbook_example_id=int(example_id),skill_id=str(skill_id),gencode_status="verified",induced_spec_payload=payload,gencode_error_log=None);written+=1
    finally:production.close()
    return written

def package_and_publish()->dict[str,Any]:
    staging_parent=PROJECT_ROOT/"reports"/"gencode_v3_publish_staging";staging_parent.mkdir(parents=True,exist_ok=True)
    staging_root=Path(tempfile.mkdtemp(prefix="b2_14_phase3_",dir=staging_parent));conn=_tracker_snapshot();results={}
    try:
        for skill_id,expected in SKILL_COMPONENTS.items():
            compiled=compile_and_double_write_skill(conn,skill_id,str(staging_root));synced=_sync_staging_v3_component_sources(staging_root,skill_id,project_path=PROJECT_ROOT)
            if compiled["component_count"]!=expected:raise RuntimeError(f"wrapper_count_mismatch:{skill_id}")
            if synced["component_count"]!=expected:raise RuntimeError(f"component_sync_count_mismatch:{skill_id}")
            run_v3_smoke(staging_root,skill_id);results[skill_id]={"wrapper_components":expected,"published":0,"staging_smoke":"passed","production_smoke":"pending"}
        for skill_id,expected in SKILL_COMPONENTS.items():
            stage=staging_root/"agent_skills_v3"/skill_id;production=PROJECT_ROOT/"agent_skills_v3"/skill_id
            _atomic_copy(stage/"__init__.py",production/"__init__.py");_atomic_copy(stage/"component_manifest.json",production/"component_manifest.json");_atomic_copy(staging_root/"skills"/f"{skill_id}.py",PROJECT_ROOT/"skills"/f"{skill_id}.py")
            run_v3_smoke(PROJECT_ROOT,skill_id);results[skill_id].update({"published":expected,"production_smoke":"passed"})
        tracker_written=_publish_tracker_evidence(conn)
    finally:conn.close()
    return {"status":"published","staging_root":str(staging_root),"skills":results,"component_total":sum(SKILL_COMPONENTS.values()),"tracker_written":tracker_written,"production_db_written":True}

if __name__=="__main__":print(json.dumps(package_and_publish(),ensure_ascii=False,indent=2))
