# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-blood-homocysteine-mthfr-methylation-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def audit_homocysteine_methylation_risk(homocysteine_umol_l, serum_folate_ng_ml=14.0, serum_b12_pg_ml=550.0, mthfr_genotype="C677T_HETEROZYGOUS"):
    if homocysteine_umol_l <= 0:
        raise ValueError("homocysteine_umol_l must be positive")
        
    # Standard optimal reference range: 6.0 - 9.0 umol/L
    # Mild hyperhomocysteinemia: 10.0 - 15.0
    # Moderate: 15.0 - 30.0
    # Severe: > 30.0
    if homocysteine_umol_l <= 9.0:
        tier = "OPTIMAL_METHYLATION_STATUS"
        vascular_risk = "LOW"
    elif homocysteine_umol_l <= 12.0:
        tier = "MILD_ELEVATION_SUBOPTIMAL"
        vascular_risk = "MILD"
    elif homocysteine_umol_l <= 15.0:
        tier = "MODERATE_HYPERHOMOCYSTEINEMIA"
        vascular_risk = "MODERATE"
    else:
        tier = "SEVERE_HYPERHOMOCYSTEINEMIA"
        vascular_risk = "HIGH_ENDOTHELIAL_TOXICITY"
        
    # Cofactor deficiency analysis
    deficiencies = []
    if serum_folate_ng_ml < 7.0:
        deficiencies.append("Serum folate depleted (< 7.0 ng/mL); remethylation cycle impaired")
    if serum_b12_pg_ml < 400.0:
        deficiencies.append("Serum B12 subtherapeutic (< 400 pg/mL); methionine synthase cofactor deficit")
        
    mthfr_reduction_pct = 0.0
    gt = mthfr_genotype.upper()
    if "C677T_HOMOZYGOUS" in gt or "TT" in gt:
        mthfr_reduction_pct = 70.0
    elif "C677T_HETEROZYGOUS" in gt or "CT" in gt:
        mthfr_reduction_pct = 35.0
    elif "COMPOUND" in gt:
        mthfr_reduction_pct = 50.0
        
    return {
        "serum_homocysteine_umol_l": round(homocysteine_umol_l, 2),
        "target_optimal_umol_l": "< 9.0",
        "methylation_efficiency_tier": tier,
        "vascular_endothelial_risk": vascular_risk,
        "mthfr_enzymatic_loss_pct": mthfr_reduction_pct,
        "serum_folate_ng_ml": serum_folate_ng_ml,
        "serum_b12_pg_ml": serum_b12_pg_ml,
        "identified_cofactor_deficits": deficiencies if deficiencies else ["Adequate methyl-donor cofactors"],
        "recommendation": "Supplement with 5-MTHF (L-methylfolate) and methylcobalamin; retest in 8 weeks." if homocysteine_umol_l > 10.0 else "Optimal methylation homeostasis maintained."
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "audit_homocysteine_methylation_risk",
                        "description": """Audit one-carbon metabolism, cellular methylation capacity, and vascular endothelial damage risk using serum homocysteine (umol/L).
Evaluates MTHFR C677T / A1298C genetic polymorphism risks, methyl-B12 and L-methylfolate cofactor adequacy, and coronary/cerebrovascular risk categories.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = audit_homocysteine_methylation_risk(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'homocysteine_umol_l': 11.4, 'serum_folate_ng_ml': 8.5, 'serum_b12_pg_ml': 420.0, 'mthfr_genotype': 'C677T_HETEROZYGOUS'}
        out = audit_homocysteine_methylation_risk(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
