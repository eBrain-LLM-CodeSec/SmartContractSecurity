# Security Audit Report: 2025-04-forte

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-no-assembly::src/Float128.sol: req-1-no-assembly::src/Float128.sol

**Requirement:** 

**Location(s):** Float128.add, Float128.decode, Float128.div, Float128.findNumberOfDigits, Float128.ge, Float128.gt, Float128.le, Float128.lt, Float128.mul, Float128.sqrt, Float128.sub, Float128.toPackedFloat, Uint512.div512x256, Uint512.mul256x256, Uint512.sqrt256, Uint512.sqrt512

**Confidence:** HIGH

**Mechanism:** Requirement forbids assembly unless overriding conditions apply. The codebase uses numerous inline assembly blocks (including Float128.add). No evidence of overriding documentation or exemptions; pragma alone does not qualify. Thus the presence of assembly violates the requirement.

**Supporting evidence:**
  - Float128.lt: Float128.lt(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#842-891) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#844-890)
  - Float128.findNumberOfDigits: Float128.findNumberOfDigits(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1167-1200) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1168-1199)
  - Float128.sub: Float128.sub(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#255-448) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#260-264)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#268-375)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#379-381)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#390-406)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#411-414)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#419-442)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#444-446)
  - Float128.div: Float128.div(packedFloat,packedFloat,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#586-687) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#587-596)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#607-641)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#648-651)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#653-686)
  - Uint512.div512x256: Uint512.div512x256(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#39-83) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#40-64)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#69-82)
  - Float128.le: Float128.le(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#899-948) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#901-947)
  - Float128.decode: Float128.decode(packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1143-1160) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1144-1159)
  - Float128.toPackedFloat: Float128.toPackedFloat(int256,int256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1083-1135) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1088-1093)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1100-1115)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1120-1124)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1126-1128)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1131-1133)
  - Float128.sqrt: Float128.sqrt(packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#695-834) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#702-717)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#750-752)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#756-832)
  - Uint512.mul256x256: Uint512.mul256x256(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#20-26) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#21-25)
  - Float128.add: Float128.add(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#60-246) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#66-173)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#177-179)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#188-204)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#209-212)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#217-240)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#242-244)
  - Float128.ge: Float128.ge(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1013-1062) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1015-1061)
  - Uint512.sqrt512: Uint512.sqrt512(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#148-227) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#155-186)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#196-212)
  - Float128.gt: Float128.gt(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#956-1005) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#958-1004)
  - Uint512.sqrt256: Uint512.sqrt256(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#92-138) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#95-125)
  - Float128.mul: Float128.mul(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#456-557) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#463-492)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#497-517)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#519-549)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#551-556)

_Determined via graph-gated Codex investigation (1 graph queries, 124s)._

## req-2-pass-l1::src/Float128.sol: req-2-pass-l1::src/Float128.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-documented::src/Float128.sol: req-2-documented::src/Float128.sol

**Requirement:** 

**Location(s):** Float128.add, Float128.decode, Float128.div, Float128.findNumberOfDigits, Float128.ge, Float128.gt, Float128.le, Float128.lt, Float128.mul, Float128.sqrt, Float128.sub, Float128.toPackedFloat, Uint512.div512x256, Uint512.mul256x256, Uint512.sqrt256, Uint512.sqrt512

**Confidence:** HIGH

**Mechanism:** The requirement demands documentation for each special construct, including assembly. Float128.add uses multiple inline assembly blocks but provides only a generic NatSpec summary with no explanation of the need for assembly, so the requirement is unmet.

**Supporting evidence:**
  - Float128.lt: Float128.lt(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#842-891) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#844-890)
  - Float128.findNumberOfDigits: Float128.findNumberOfDigits(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1167-1200) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1168-1199)
  - Float128.sub: Float128.sub(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#255-448) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#260-264)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#268-375)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#379-381)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#390-406)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#411-414)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#419-442)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#444-446)
  - Float128.div: Float128.div(packedFloat,packedFloat,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#586-687) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#587-596)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#607-641)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#648-651)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#653-686)
  - Uint512.div512x256: Uint512.div512x256(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#39-83) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#40-64)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#69-82)
  - Float128.le: Float128.le(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#899-948) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#901-947)
  - Float128.decode: Float128.decode(packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1143-1160) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1144-1159)
  - Float128.toPackedFloat: Float128.toPackedFloat(int256,int256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1083-1135) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1088-1093)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1100-1115)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1120-1124)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1126-1128)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1131-1133)
  - Float128.sqrt: Float128.sqrt(packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#695-834) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#702-717)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#750-752)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#756-832)
  - Uint512.mul256x256: Uint512.mul256x256(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#20-26) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#21-25)
  - Float128.add: Float128.add(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#60-246) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#66-173)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#177-179)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#188-204)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#209-212)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#217-240)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#242-244)
  - Float128.ge: Float128.ge(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1013-1062) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#1015-1061)
  - Uint512.sqrt512: Uint512.sqrt512(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#148-227) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#155-186)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#196-212)
  - Float128.gt: Float128.gt(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#956-1005) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#958-1004)
  - Uint512.sqrt256: Uint512.sqrt256(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#92-138) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol#95-125)
  - Float128.mul: Float128.mul(packedFloat,packedFloat) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#456-557) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#463-492)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#497-517)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#519-549)
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol#551-556)
  - Float128.mul: makes an external call
  - Float128.div: makes an external call
  - Float128.sqrt: makes an external call
  - Float128.sqrt: makes an external call
  - Uint512.mul256x256: * operation, inside unchecked{} block
  - Uint512.mul256x256: - operation, inside unchecked{} block
  - Uint512.mul256x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: + operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: - operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.lt: * operation, inside unchecked{} block
  - Float128.lt: - operation, inside unchecked{} block
  - Float128.lt: * operation, inside unchecked{} block
  - Float128.lt: - operation, inside unchecked{} block
  - Float128.le: * operation, inside unchecked{} block
  - Float128.le: - operation, inside unchecked{} block
  - Float128.le: * operation, inside unchecked{} block
  - Float128.le: - operation, inside unchecked{} block
  - Float128.gt: * operation, inside unchecked{} block
  - Float128.gt: - operation, inside unchecked{} block
  - Float128.gt: * operation, inside unchecked{} block
  - Float128.gt: - operation, inside unchecked{} block
  - Float128.ge: * operation, inside unchecked{} block
  - Float128.ge: - operation, inside unchecked{} block
  - Float128.ge: * operation, inside unchecked{} block
  - Float128.ge: - operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: ** operation, inside unchecked{} block
  - Float128.toPackedFloat: * operation, inside unchecked{} block
  - Float128.toPackedFloat: ** operation, inside unchecked{} block
  - Float128.toPackedFloat: * operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block

_Determined via graph-gated Codex investigation (1 graph queries, 192s)._

## req-2-overflow-underflow::src/Float128.sol: req-2-overflow-underflow::src/Float128.sol

**Requirement:** 

**Location(s):** Float128.add, Float128.decode, Float128.div, Float128.findNumberOfDigits, Float128.ge, Float128.gt, Float128.le, Float128.lt, Float128.mul, Float128.sqrt, Float128.sub, Float128.toPackedFloat, Uint512.div512x256, Uint512.mul256x256, Uint512.sqrt256, Uint512.sqrt512

**Confidence:** MEDIUM

**Mechanism:** Float128.add (and related normalization/encoding) uses inline assembly to scale mantissas by exp(BASE, k) where k comes from unbounded exponent or digit differences. With allowed exponents up to ±8192 or oversized mantissas, 10**k exceeds 256-bit, causing wraparound with no checks or reverts. No saturation or SafeMath-equivalent protections exist, violating the overflow/underflow safety requirement.

**Supporting evidence:**
  - Uint512.mul256x256: * operation, inside unchecked{} block
  - Uint512.mul256x256: - operation, inside unchecked{} block
  - Uint512.mul256x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: + operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: - operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.div512x256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: * operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt256: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: - operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: + operation, inside unchecked{} block
  - Uint512.sqrt512: * operation, inside unchecked{} block
  - Uint512.sqrt512: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: * operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: ** operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: - operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.add: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: * operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: ** operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: - operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.sub: + operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: * operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: - operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.mul: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: * operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: - operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.div: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: * operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: - operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.sqrt: + operation, inside unchecked{} block
  - Float128.lt: * operation, inside unchecked{} block
  - Float128.lt: - operation, inside unchecked{} block
  - Float128.lt: * operation, inside unchecked{} block
  - Float128.lt: - operation, inside unchecked{} block
  - Float128.le: * operation, inside unchecked{} block
  - Float128.le: - operation, inside unchecked{} block
  - Float128.le: * operation, inside unchecked{} block
  - Float128.le: - operation, inside unchecked{} block
  - Float128.gt: * operation, inside unchecked{} block
  - Float128.gt: - operation, inside unchecked{} block
  - Float128.gt: * operation, inside unchecked{} block
  - Float128.gt: - operation, inside unchecked{} block
  - Float128.ge: * operation, inside unchecked{} block
  - Float128.ge: - operation, inside unchecked{} block
  - Float128.ge: * operation, inside unchecked{} block
  - Float128.ge: - operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: ** operation, inside unchecked{} block
  - Float128.toPackedFloat: * operation, inside unchecked{} block
  - Float128.toPackedFloat: ** operation, inside unchecked{} block
  - Float128.toPackedFloat: * operation, inside unchecked{} block
  - Float128.toPackedFloat: - operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.toPackedFloat: + operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.decode: - operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block
  - Float128.findNumberOfDigits: + operation, inside unchecked{} block

_Determined via graph-gated Codex investigation (1 graph queries, 319s)._

## req-3-pass-l2::src/Float128.sol: req-3-pass-l2::src/Float128.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-all-valid-inputs::src/Float128.sol: req-3-all-valid-inputs::src/Float128.sol

**Requirement:** 

**Location(s):** Float128.add, Float128.decode, Float128.div, Float128.divL, Float128.eq, Float128.findNumberOfDigits, Float128.ge, Float128.gt, Float128.le, Float128.lt, Float128.mul, Float128.sqrt, Float128.sub, Float128.toPackedFloat, Uint512.div512x256, Uint512.mul256x256, Uint512.sqrt256, Uint512.sqrt512

**Confidence:** MEDIUM

**Mechanism:** The add routine performs complex arithmetic directly on the raw packed bits with no validation of exponent bounds, mantissa size, or flag consistency; malformed inputs are neither rejected nor sanitized, so the code fails the requirement to validate and correctly process malformed inputs.

**Supporting evidence:**
  - Uint512.mul256x256: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Uint512.div512x256: none of this function's parameters (['a0', 'a1', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Uint512.sqrt256: none of this function's parameters (['x']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Uint512.sqrt512: none of this function's parameters (['a0', 'a1']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.add: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.sub: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.mul: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.div: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.divL: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.div: none of this function's parameters (['a', 'b', 'rL']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.sqrt: none of this function's parameters (['a']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.lt: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.le: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.gt: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.ge: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.eq: none of this function's parameters (['a', 'b']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.toPackedFloat: none of this function's parameters (['exponent', 'mantissa']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.decode: none of this function's parameters (['float']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling
  - Float128.findNumberOfDigits: none of this function's parameters (['x']) are referenced in any require()/assert() call -- evidence of no input validation, not a proof of malformed-input handling

_Determined via graph-gated Codex investigation (1 graph queries, 159s)._

## req-3-event-on-state-change::src/Float128.sol: req-3-event-on-state-change::src/Float128.sol

**Requirement:** 

**Location(s):** Float128.slitherConstructorConstantVariables

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Float128.slitherConstructorConstantVariables: writes state but emits no event

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-document-threats::src/Float128.sol: req-3-document-threats::src/Float128.sol

**Requirement:** 

**Location(s):** 2025-04-forte, Float128.sol, Float128.sol (NatSpec), README.md

**Confidence:** HIGH

**Mechanism:** Searched repository (README, SECURITY.md, docs, src) and found no threat model describing threats, assumptions, responses, or outcomes. Requirement mandates such documentation; absence constitutes failure.

**Supporting evidence:**
  - README.md: # Forte audit details
- Total Prize Pool: $40,000 in USDC
  - HM awards: up to $32,600 in USDC 
    - If no valid Highs or Mediums are found, the HM pool is $0 
  - QA awards: $1,400 in USDC
  - Judge awards: $3,300 in USDC
  - Validator awards: $2,200 in USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts April 1, 2025 20:00 UTC
- Ends April 11, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments: 
- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-03-thrackle/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

### Exponent / Mantissa Limitations

Floating number representations with exponents greater than `3000` or less than `-3000` are not within acceptable bounds for this library. Failure to abide by this limitation may result in precision loss and/or arithmetic overflows/underflows.

Additionally, the maximum digits the library is meant to handle accurately are `72`. Any digits higher than that value are not expected to be secure and may result in precision loss, arithmetic overflows/underflows, or other unforeseen errors.

### Acceptable Errors in Operations

The library's arithmetic operations' errors have been calculated against results from Python's Decimal library. The errors are defined in Units in the Last Place (ULP):

| Operation              | Max Error (ULP) |
| ---------------------- | ---------------- |
| Addition (add)         | 1                |
| Subtraction (sub)      | 1                |
| Multiplication (mul)   | 0                |
| Division (div/divL)    | 0                |
| Square root (sqrt)     | 0                |
| Natural Logarithm (ln)\* | 99                |

> [!WARNING]
> \* The precision of the Natural Logarithm function (ln) is not guaranteed for numbers that are in the $(1.0,1.1)$ range. For numbers with `≤38` significant digits, errors are generally limited to `199` ULP. However, numbers with `>38` significant digits may exhibit relative errors exceeding 50% in extreme cases.

# Overview

## Float128 Solidity Library

This is a signed floating-point library optimized for Solidity.

### General Floating-Point Concepts

A floating point number is a way to represent numbers in an efficient way. It is composed of 3 elements:

- **Mantissa**: The significant digits of the number. It is an integer that is later multiplied by the base elevated to the exponent's power.
- **Base**: Generally either 2 or 10. It determines the base of the multiplier factor.
- **Exponent**: The amount of times the base will multiply/divide itself to later be applied to the mantissa.

Some examples:

- -0.0001 can be expressed as -1 x $10^{-4}$.

  - Mantissa: -1
  - Base: 10
  - Exponent: -4

- 2222000000000000 can be expressed as 2222 x $10^{12}$.
  - Mantissa: 2222
  - Base: 10
  - Exponent: 12

Floating point numbers can represent the same number in infinite ways by playing with the exponent. For instance, the first example could be also represented by -10 x $10^{-5}$, -100 x $10^{-6}$, -1000 x $10^{-7}$, etc.

#### Library main features

- Base: 10
- Significant digits: 38 or 72
- Exponent range: -8192 and +8191
- Maximum exponent for 38-digit mantissas: -18

#### Available operations

- Addition (`add`)
- Subtraction (`sub`)
- Multiplication (`mul`)
- Division (`div`/`divL`)
- Square root (`sqrt`)
- Natural Logarithm (`ln`)
- Less Than (`lt`)
- Less Than Or Equal To (`le`)
- Greater Than (`gt`)
- Greater Than Or Equal To (`ge`)
- Equal (`eq`)

### Types

#### packedFloat:

This type uses a `uint256` under the hood:

```Solidity
type packedFloat is uint256;
```

##### Bitmap:

| Bit range | Reserved for    |
| --------- | --------------- |
| 255 - 242 | EXPONENT        |
| 241       | L_MANTISSA_FLAG |
| 240       | MANTISSA_SIGN   |
| 239 - 0   | L_MANTISSA      |
| 128 - 0   | M_MANTISSA      |

#### Mantissa sizes:

The packedFloat can handle 2 different lengths of mantissas:

- **Medium-size mantissas (38 digits)**: This is the more gas efficient representation of a floating-point number when it comes to arithmetic since all the operations, including results, will fit inside a 256-bit word. This representation, however, offers a limited storage for the number which might not be enough for ocasions where very high precision is required.

- **Large-size mantissas (72 digits)**: This is the more precise representation of a floatint-point number since it can store 72 significand digits of information. The trade-off is higher gas consumption as its arithmetic will require 512-bit multiplication and division which can be expensive operations.

#### Maximum exponent and mantissa-size autoscaling

The library counts with a `MAXIMUM_EXPONENT` constant to keep a minimum amount of decimals of precision before it autoscales to a large mantissa. This is done to guarantee a minimum precision level among operations.

For example, if the result of an arithmetic operation results in a number big enough to have its exponent bigger than `MAXIMUM_EXPONENT`, then the result will be given in a large-mantissa format to make sure that we can store enough information about the resulting number with at least our minimum amount of decimals of precision. This also works the other way around where operations between large-mantissa numbers result in a value that has its exponent small enough to be stored as a medium-size mantissa number.

In
  - Float128.sol (NatSpec): /**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */
  - Float128.sol (NatSpec): /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the difference between 2 signed floating point numbers
     * @param a the minuend
     * @param b the subtrahend
     * @return r the result of a - b
     * @notice this version of the function uses only the packedFloat type
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the product of 2 signed floating point numbers
     * @param a the multiplicand
     * @param b the multiplier
     * @return r the result of a * b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers which results in a large mantissa (72 digits) for better precision
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the remainder of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @param rL Large mantissa flag for the result. If true, the result will be force to use 72 digits for the mansitssa
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev get the square root of a signed floating point
     * @notice only positive numbers can have their square root calculated through this function
     * @param a the numerator to get the square root of
     * @return r the result of √a
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a < b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than or equals to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a <= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a > b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than or equal to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a >= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs an equality comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a == b
     */
  - Float128.sol (NatSpec): /**
     * @dev encodes a pair of signed integer values describing a floating point number into a packedFloat
     * Examples: 1234.567 can be expressed as: 123456 x 10**(-3), or 1234560 x 10**(-4), or 12345600 x 10**(-5), etc.
     * @notice the mantissa can hold a maximum of 38 or 72 digits. Any number in between or more digits will lose precision.
     * @param mantissa the integer that holds the mantissa digits (38 or 72 digits max)
     * @param exponent the exponent of the floating point number (between -8192 and +8191)
     * @return float the encoded number. This value will ocupy a single 256-bit word and will hold the normalized
     * version of the floating-point number (shifts the exponent enough times to have exactly 38 or 72 significant digits)
     */
  - Float128.sol (NatSpec): /**
     * @dev decodes a packedFloat into its mantissa and its exponent
     * @param float the floating-point number expressed as a packedFloat to decode
     * @return mantissa the 38 mantissa digits of the floating-point number
     * @return exponent the exponent of the floating-point number
     */
  - Float128.sol (NatSpec): /// we use 2's complement for mantissa sign
  - Float128.sol (NatSpec): /**
     * @dev finds the amount of digits of a number
     * @param x the number
     * @return log the amount of digits of x
     */
  - Float128.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Uint512} from "../lib/Uint512.sol";
import {packedFloat} from "./Types.sol";

/**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */

library Float128 {
    uint constant MANTISSA_MASK = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    uint constant MANTISSA_SIGN_MASK = 0x1000000000000000000000000000000000000000000000000000000000000;
    uint constant MANTISSA_L_FLAG_MASK = 0x2000000000000000000000000000000000000000000000000000000000000;
    uint constant EXPONENT_MASK = 0xfffc000000000000000000000000000000000000000000000000000000000000;
    uint constant TWO_COMPLEMENT_SIGN_MASK = 0x8000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE = 10;
    uint constant ZERO_OFFSET = 8192;
    uint constant ZERO_OFFSET_MINUS_1 = 8191;
    uint constant EXPONENT_BIT = 242;
    uint constant MAX_DIGITS_M = 38;
    uint constant MAX_DIGITS_M_X_2 = 76;
    uint constant MAX_DIGITS_M_MINUS_1 = 37;
    uint constant MAX_DIGITS_M_PLUS_1 = 39;
    uint constant MAX_DIGITS_L = 72;
    uint constant MAX_DIGITS_L_MINUS_1 = 71;
    uint constant MAX_DIGITS_L_PLUS_1 = 73;
    uint constant DIGIT_DIFF_L_M = 34;
    uint constant DIGIT_DIFF_L_M_PLUS_1 = 35;
    uint constant DIGIT_DIFF_76_L_MINUS_1 = 3;
    uint constant DIGIT_DIFF_76_L = 4;
    uint constant DIGIT_DIFF_76_L_PLUS_1 = 5;
    uint constant MAX_M_DIGIT_NUMBER = 99999999999999999999999999999999999999;
    uint constant MIN_M_DIGIT_NUMBER = 10000000000000000000000000000000000000;
    uint constant MAX_L_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MIN_L_DIGIT_NUMBER = 100000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_L = 1000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF = 10000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF_PLUS_1 = 100000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_MINUS_1 = 10000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M = 100000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_PLUS_1 = 1000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_X_2 =
        10000000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIFF_76_L_MINUS_1 = 1_000;
    uint constant BASE_TO_THE_DIFF_76_L = 10_000;
    uint constant BASE_TO_THE_DIFF_76_L_PLUS_1 = 100_000;
    uint constant MAX_75_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MAX_76_DIGIT_NUMBER = 9999999999999999999999999999999999999999999999999999999999999999999999999999;
    int constant MAXIMUM_EXPONENT = -18; // guarantees all results will have at least 18 decimals in the M size. Autoscales to L if necessary

    /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
    function add(packedFloat a, packedFloat b) internal pure returns (packedFloat r) {
        uint addition;
        bool isSubtraction;
        bool sameExponent;
        if (packedFloat.unwrap(a) == 0) return b;
        if (packedFloat.unwrap(b) == 0) return a;
        assembly {
            let aL := gt(and(a, MANTISSA_L_FLAG_MASK), 0)
            let bL := gt(and(b, MANTISSA_L_FLAG_MASK), 0)
            isSubtraction := xor(and(a, MANTISSA_SIGN_MASK), and(b, MANTISSA_SIGN_MASK))
            // we extract the exponent and mantissas for both
            let aExp := and(a, EXPONENT_MASK)
            let bExp := and(b, EXPONENT_MASK)
            let aMan := and(a, MANTISSA_MASK)
            let bMan := and(b, MANTISSA_MASK)
            if iszero(or(aL, bL)) {
                // we add 38 digits of precision in the case of subtraction
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    sameExponent := 1
                }
            }
            if or(aL, bL) {
                // we make sure both of them are size L before continuing
                if iszero(aL) {
                    aMan := mul(aMan, BASE_TO_THE_DIGIT_DIFF)
                    aExp := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                if iszero(bL) {
                    bMan := mul(bMan, BASE_TO_THE_DIGIT_DIFF)
                    bExp := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                // we adjust the significant digits and set the exponent of the result
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                // // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BA
  - 2025-04-forte: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 274s)._

## req-3-consistent-solidity-output::src/Float128.sol: req-3-consistent-solidity-output::src/Float128.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.24

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - pragma solidity^0.8.24: pragma '^0.8.24' is a range, not an exact pin
  - pragma solidity^0.8.24: pragma '^0.8.24' is a range, not an exact pin
  - pragma solidity^0.8.24: pragma '^0.8.24' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-use-latest-compiler::src/Float128.sol: req-R-use-latest-compiler::src/Float128.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - compiler config: solc 0.8.24 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-clean-code::src/Float128.sol: req-R-clean-code::src/Float128.sol

**Requirement:** 

**Location(s):** 2025-04-forte, Float128.sol, Float128.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** The Float128 library relies on very large inline assembly blocks using terse variable names and numerous magic constants with minimal commentary or decomposition. Key arithmetic functions span hundreds of lines without modular helpers or explanatory notes, making the code difficult to read and understand, thus not meeting the clarity/legibility expectation.

**Supporting evidence:**
  - README.md: # Forte audit details
- Total Prize Pool: $40,000 in USDC
  - HM awards: up to $32,600 in USDC 
    - If no valid Highs or Mediums are found, the HM pool is $0 
  - QA awards: $1,400 in USDC
  - Judge awards: $3,300 in USDC
  - Validator awards: $2,200 in USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts April 1, 2025 20:00 UTC
- Ends April 11, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments: 
- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-03-thrackle/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

### Exponent / Mantissa Limitations

Floating number representations with exponents greater than `3000` or less than `-3000` are not within acceptable bounds for this library. Failure to abide by this limitation may result in precision loss and/or arithmetic overflows/underflows.

Additionally, the maximum digits the library is meant to handle accurately are `72`. Any digits higher than that value are not expected to be secure and may result in precision loss, arithmetic overflows/underflows, or other unforeseen errors.

### Acceptable Errors in Operations

The library's arithmetic operations' errors have been calculated against results from Python's Decimal library. The errors are defined in Units in the Last Place (ULP):

| Operation              | Max Error (ULP) |
| ---------------------- | ---------------- |
| Addition (add)         | 1                |
| Subtraction (sub)      | 1                |
| Multiplication (mul)   | 0                |
| Division (div/divL)    | 0                |
| Square root (sqrt)     | 0                |
| Natural Logarithm (ln)\* | 99                |

> [!WARNING]
> \* The precision of the Natural Logarithm function (ln) is not guaranteed for numbers that are in the $(1.0,1.1)$ range. For numbers with `≤38` significant digits, errors are generally limited to `199` ULP. However, numbers with `>38` significant digits may exhibit relative errors exceeding 50% in extreme cases.

# Overview

## Float128 Solidity Library

This is a signed floating-point library optimized for Solidity.

### General Floating-Point Concepts

A floating point number is a way to represent numbers in an efficient way. It is composed of 3 elements:

- **Mantissa**: The significant digits of the number. It is an integer that is later multiplied by the base elevated to the exponent's power.
- **Base**: Generally either 2 or 10. It determines the base of the multiplier factor.
- **Exponent**: The amount of times the base will multiply/divide itself to later be applied to the mantissa.

Some examples:

- -0.0001 can be expressed as -1 x $10^{-4}$.

  - Mantissa: -1
  - Base: 10
  - Exponent: -4

- 2222000000000000 can be expressed as 2222 x $10^{12}$.
  - Mantissa: 2222
  - Base: 10
  - Exponent: 12

Floating point numbers can represent the same number in infinite ways by playing with the exponent. For instance, the first example could be also represented by -10 x $10^{-5}$, -100 x $10^{-6}$, -1000 x $10^{-7}$, etc.

#### Library main features

- Base: 10
- Significant digits: 38 or 72
- Exponent range: -8192 and +8191
- Maximum exponent for 38-digit mantissas: -18

#### Available operations

- Addition (`add`)
- Subtraction (`sub`)
- Multiplication (`mul`)
- Division (`div`/`divL`)
- Square root (`sqrt`)
- Natural Logarithm (`ln`)
- Less Than (`lt`)
- Less Than Or Equal To (`le`)
- Greater Than (`gt`)
- Greater Than Or Equal To (`ge`)
- Equal (`eq`)

### Types

#### packedFloat:

This type uses a `uint256` under the hood:

```Solidity
type packedFloat is uint256;
```

##### Bitmap:

| Bit range | Reserved for    |
| --------- | --------------- |
| 255 - 242 | EXPONENT        |
| 241       | L_MANTISSA_FLAG |
| 240       | MANTISSA_SIGN   |
| 239 - 0   | L_MANTISSA      |
| 128 - 0   | M_MANTISSA      |

#### Mantissa sizes:

The packedFloat can handle 2 different lengths of mantissas:

- **Medium-size mantissas (38 digits)**: This is the more gas efficient representation of a floating-point number when it comes to arithmetic since all the operations, including results, will fit inside a 256-bit word. This representation, however, offers a limited storage for the number which might not be enough for ocasions where very high precision is required.

- **Large-size mantissas (72 digits)**: This is the more precise representation of a floatint-point number since it can store 72 significand digits of information. The trade-off is higher gas consumption as its arithmetic will require 512-bit multiplication and division which can be expensive operations.

#### Maximum exponent and mantissa-size autoscaling

The library counts with a `MAXIMUM_EXPONENT` constant to keep a minimum amount of decimals of precision before it autoscales to a large mantissa. This is done to guarantee a minimum precision level among operations.

For example, if the result of an arithmetic operation results in a number big enough to have its exponent bigger than `MAXIMUM_EXPONENT`, then the result will be given in a large-mantissa format to make sure that we can store enough information about the resulting number with at least our minimum amount of decimals of precision. This also works the other way around where operations between large-mantissa numbers result in a value that has its exponent small enough to be stored as a medium-size mantissa number.

In
  - Float128.sol (NatSpec): /**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */
  - Float128.sol (NatSpec): /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the difference between 2 signed floating point numbers
     * @param a the minuend
     * @param b the subtrahend
     * @return r the result of a - b
     * @notice this version of the function uses only the packedFloat type
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the product of 2 signed floating point numbers
     * @param a the multiplicand
     * @param b the multiplier
     * @return r the result of a * b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers which results in a large mantissa (72 digits) for better precision
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the remainder of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @param rL Large mantissa flag for the result. If true, the result will be force to use 72 digits for the mansitssa
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev get the square root of a signed floating point
     * @notice only positive numbers can have their square root calculated through this function
     * @param a the numerator to get the square root of
     * @return r the result of √a
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a < b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than or equals to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a <= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a > b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than or equal to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a >= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs an equality comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a == b
     */
  - Float128.sol (NatSpec): /**
     * @dev encodes a pair of signed integer values describing a floating point number into a packedFloat
     * Examples: 1234.567 can be expressed as: 123456 x 10**(-3), or 1234560 x 10**(-4), or 12345600 x 10**(-5), etc.
     * @notice the mantissa can hold a maximum of 38 or 72 digits. Any number in between or more digits will lose precision.
     * @param mantissa the integer that holds the mantissa digits (38 or 72 digits max)
     * @param exponent the exponent of the floating point number (between -8192 and +8191)
     * @return float the encoded number. This value will ocupy a single 256-bit word and will hold the normalized
     * version of the floating-point number (shifts the exponent enough times to have exactly 38 or 72 significant digits)
     */
  - Float128.sol (NatSpec): /**
     * @dev decodes a packedFloat into its mantissa and its exponent
     * @param float the floating-point number expressed as a packedFloat to decode
     * @return mantissa the 38 mantissa digits of the floating-point number
     * @return exponent the exponent of the floating-point number
     */
  - Float128.sol (NatSpec): /// we use 2's complement for mantissa sign
  - Float128.sol (NatSpec): /**
     * @dev finds the amount of digits of a number
     * @param x the number
     * @return log the amount of digits of x
     */
  - Float128.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Uint512} from "../lib/Uint512.sol";
import {packedFloat} from "./Types.sol";

/**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */

library Float128 {
    uint constant MANTISSA_MASK = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    uint constant MANTISSA_SIGN_MASK = 0x1000000000000000000000000000000000000000000000000000000000000;
    uint constant MANTISSA_L_FLAG_MASK = 0x2000000000000000000000000000000000000000000000000000000000000;
    uint constant EXPONENT_MASK = 0xfffc000000000000000000000000000000000000000000000000000000000000;
    uint constant TWO_COMPLEMENT_SIGN_MASK = 0x8000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE = 10;
    uint constant ZERO_OFFSET = 8192;
    uint constant ZERO_OFFSET_MINUS_1 = 8191;
    uint constant EXPONENT_BIT = 242;
    uint constant MAX_DIGITS_M = 38;
    uint constant MAX_DIGITS_M_X_2 = 76;
    uint constant MAX_DIGITS_M_MINUS_1 = 37;
    uint constant MAX_DIGITS_M_PLUS_1 = 39;
    uint constant MAX_DIGITS_L = 72;
    uint constant MAX_DIGITS_L_MINUS_1 = 71;
    uint constant MAX_DIGITS_L_PLUS_1 = 73;
    uint constant DIGIT_DIFF_L_M = 34;
    uint constant DIGIT_DIFF_L_M_PLUS_1 = 35;
    uint constant DIGIT_DIFF_76_L_MINUS_1 = 3;
    uint constant DIGIT_DIFF_76_L = 4;
    uint constant DIGIT_DIFF_76_L_PLUS_1 = 5;
    uint constant MAX_M_DIGIT_NUMBER = 99999999999999999999999999999999999999;
    uint constant MIN_M_DIGIT_NUMBER = 10000000000000000000000000000000000000;
    uint constant MAX_L_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MIN_L_DIGIT_NUMBER = 100000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_L = 1000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF = 10000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF_PLUS_1 = 100000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_MINUS_1 = 10000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M = 100000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_PLUS_1 = 1000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_X_2 =
        10000000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIFF_76_L_MINUS_1 = 1_000;
    uint constant BASE_TO_THE_DIFF_76_L = 10_000;
    uint constant BASE_TO_THE_DIFF_76_L_PLUS_1 = 100_000;
    uint constant MAX_75_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MAX_76_DIGIT_NUMBER = 9999999999999999999999999999999999999999999999999999999999999999999999999999;
    int constant MAXIMUM_EXPONENT = -18; // guarantees all results will have at least 18 decimals in the M size. Autoscales to L if necessary

    /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
    function add(packedFloat a, packedFloat b) internal pure returns (packedFloat r) {
        uint addition;
        bool isSubtraction;
        bool sameExponent;
        if (packedFloat.unwrap(a) == 0) return b;
        if (packedFloat.unwrap(b) == 0) return a;
        assembly {
            let aL := gt(and(a, MANTISSA_L_FLAG_MASK), 0)
            let bL := gt(and(b, MANTISSA_L_FLAG_MASK), 0)
            isSubtraction := xor(and(a, MANTISSA_SIGN_MASK), and(b, MANTISSA_SIGN_MASK))
            // we extract the exponent and mantissas for both
            let aExp := and(a, EXPONENT_MASK)
            let bExp := and(b, EXPONENT_MASK)
            let aMan := and(a, MANTISSA_MASK)
            let bMan := and(b, MANTISSA_MASK)
            if iszero(or(aL, bL)) {
                // we add 38 digits of precision in the case of subtraction
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    sameExponent := 1
                }
            }
            if or(aL, bL) {
                // we make sure both of them are size L before continuing
                if iszero(aL) {
                    aMan := mul(aMan, BASE_TO_THE_DIGIT_DIFF)
                    aExp := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                if iszero(bL) {
                    bMan := mul(bMan, BASE_TO_THE_DIGIT_DIFF)
                    bExp := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                // we adjust the significant digits and set the exponent of the result
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                // // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BA
  - 2025-04-forte: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (1 graph queries, 158s)._

## req-R-define-license::src/Float128.sol: req-R-define-license::src/Float128.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Base.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Script.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdAssertions.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdChains.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdCheats.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdError.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdInvariant.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdJson.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdMath.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdStorage.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdStyle.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdToml.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdUtils.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Test.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Vm.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/console.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/console2.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC1155.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC165.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC20.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC4626.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC721.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IMulticall3.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/safeconsole.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdChains.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdError.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdJson.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStyle.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdToml.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/Vm.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationScript.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationScriptBase.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationTest.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationTestBase.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Ln.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Types.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatUtils.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/gasReport/GasHelpers.sol, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/gasReport/GasReport.t.sol, LICENSE.md

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/Uint512.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Base.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Script.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdAssertions.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdChains.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdCheats.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdError.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdInvariant.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdJson.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdMath.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdStorage.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdStyle.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdToml.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/StdUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Test.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/Vm.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/console.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/console2.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC1155.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC165.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC20.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC4626.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IERC721.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/interfaces/IMulticall3.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/src/safeconsole.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdChains.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdError.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdJson.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStyle.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdToml.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/Vm.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationScript.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationScriptBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationTest.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/compilation/CompilationTestBase.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Float128.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Ln.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/src/Types.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatUtils.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/gasReport/GasHelpers.sol: SPDX-License-Identifier found
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/gasReport/GasReport.t.sol: SPDX-License-Identifier found
  - LICENSE.md: LICENSE file present at repo root

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-notify-news::src/Float128.sol: req-R-notify-news::src/Float128.sol

**Requirement:** 

**Location(s):** 2025-04-forte, Float128.sol, Float128.sol (NatSpec), README.md

**Confidence:** MEDIUM

**Mechanism:** The repository’s only disclosure guidance directs reporters to email the project team privately; no documentation refers to notifying the EthTrust Working Group or any broader channel as required. Searches across README, docs, and Float128 NatSpec found no mention of the required reporting path, so the requirement is not met.

**Supporting evidence:**
  - README.md: # Forte audit details
- Total Prize Pool: $40,000 in USDC
  - HM awards: up to $32,600 in USDC 
    - If no valid Highs or Mediums are found, the HM pool is $0 
  - QA awards: $1,400 in USDC
  - Judge awards: $3,300 in USDC
  - Validator awards: $2,200 in USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts April 1, 2025 20:00 UTC
- Ends April 11, 2025 20:00 UTC

**Note re: risk level upgrades/downgrades**

Two important notes about judging phase risk adjustments: 
- High- or Medium-risk submissions downgraded to Low-risk (QA) will be ineligible for awards.
- Upgrading a Low-risk finding from a QA report to a Medium- or High-risk finding is not supported.

As such, wardens are encouraged to select the appropriate risk level carefully during the submission phase.

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2025-03-thrackle/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a publicly known issue and is ineligible for awards._

### Exponent / Mantissa Limitations

Floating number representations with exponents greater than `3000` or less than `-3000` are not within acceptable bounds for this library. Failure to abide by this limitation may result in precision loss and/or arithmetic overflows/underflows.

Additionally, the maximum digits the library is meant to handle accurately are `72`. Any digits higher than that value are not expected to be secure and may result in precision loss, arithmetic overflows/underflows, or other unforeseen errors.

### Acceptable Errors in Operations

The library's arithmetic operations' errors have been calculated against results from Python's Decimal library. The errors are defined in Units in the Last Place (ULP):

| Operation              | Max Error (ULP) |
| ---------------------- | ---------------- |
| Addition (add)         | 1                |
| Subtraction (sub)      | 1                |
| Multiplication (mul)   | 0                |
| Division (div/divL)    | 0                |
| Square root (sqrt)     | 0                |
| Natural Logarithm (ln)\* | 99                |

> [!WARNING]
> \* The precision of the Natural Logarithm function (ln) is not guaranteed for numbers that are in the $(1.0,1.1)$ range. For numbers with `≤38` significant digits, errors are generally limited to `199` ULP. However, numbers with `>38` significant digits may exhibit relative errors exceeding 50% in extreme cases.

# Overview

## Float128 Solidity Library

This is a signed floating-point library optimized for Solidity.

### General Floating-Point Concepts

A floating point number is a way to represent numbers in an efficient way. It is composed of 3 elements:

- **Mantissa**: The significant digits of the number. It is an integer that is later multiplied by the base elevated to the exponent's power.
- **Base**: Generally either 2 or 10. It determines the base of the multiplier factor.
- **Exponent**: The amount of times the base will multiply/divide itself to later be applied to the mantissa.

Some examples:

- -0.0001 can be expressed as -1 x $10^{-4}$.

  - Mantissa: -1
  - Base: 10
  - Exponent: -4

- 2222000000000000 can be expressed as 2222 x $10^{12}$.
  - Mantissa: 2222
  - Base: 10
  - Exponent: 12

Floating point numbers can represent the same number in infinite ways by playing with the exponent. For instance, the first example could be also represented by -10 x $10^{-5}$, -100 x $10^{-6}$, -1000 x $10^{-7}$, etc.

#### Library main features

- Base: 10
- Significant digits: 38 or 72
- Exponent range: -8192 and +8191
- Maximum exponent for 38-digit mantissas: -18

#### Available operations

- Addition (`add`)
- Subtraction (`sub`)
- Multiplication (`mul`)
- Division (`div`/`divL`)
- Square root (`sqrt`)
- Natural Logarithm (`ln`)
- Less Than (`lt`)
- Less Than Or Equal To (`le`)
- Greater Than (`gt`)
- Greater Than Or Equal To (`ge`)
- Equal (`eq`)

### Types

#### packedFloat:

This type uses a `uint256` under the hood:

```Solidity
type packedFloat is uint256;
```

##### Bitmap:

| Bit range | Reserved for    |
| --------- | --------------- |
| 255 - 242 | EXPONENT        |
| 241       | L_MANTISSA_FLAG |
| 240       | MANTISSA_SIGN   |
| 239 - 0   | L_MANTISSA      |
| 128 - 0   | M_MANTISSA      |

#### Mantissa sizes:

The packedFloat can handle 2 different lengths of mantissas:

- **Medium-size mantissas (38 digits)**: This is the more gas efficient representation of a floating-point number when it comes to arithmetic since all the operations, including results, will fit inside a 256-bit word. This representation, however, offers a limited storage for the number which might not be enough for ocasions where very high precision is required.

- **Large-size mantissas (72 digits)**: This is the more precise representation of a floatint-point number since it can store 72 significand digits of information. The trade-off is higher gas consumption as its arithmetic will require 512-bit multiplication and division which can be expensive operations.

#### Maximum exponent and mantissa-size autoscaling

The library counts with a `MAXIMUM_EXPONENT` constant to keep a minimum amount of decimals of precision before it autoscales to a large mantissa. This is done to guarantee a minimum precision level among operations.

For example, if the result of an arithmetic operation results in a number big enough to have its exponent bigger than `MAXIMUM_EXPONENT`, then the result will be given in a large-mantissa format to make sure that we can store enough information about the resulting number with at least our minimum amount of decimals of precision. This also works the other way around where operations between large-mantissa numbers result in a value that has its exponent small enough to be stored as a medium-size mantissa number.

In
  - Float128.sol (NatSpec): /**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */
  - Float128.sol (NatSpec): /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the difference between 2 signed floating point numbers
     * @param a the minuend
     * @param b the subtrahend
     * @return r the result of a - b
     * @notice this version of the function uses only the packedFloat type
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the product of 2 signed floating point numbers
     * @param a the multiplicand
     * @param b the multiplier
     * @return r the result of a * b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the quotient of 2 signed floating point numbers which results in a large mantissa (72 digits) for better precision
     * @param a the numerator
     * @param b the denominator
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev gets the remainder of 2 signed floating point numbers
     * @param a the numerator
     * @param b the denominator
     * @param rL Large mantissa flag for the result. If true, the result will be force to use 72 digits for the mansitssa
     * @return r the result of a / b
     */
  - Float128.sol (NatSpec): /**
     * @dev get the square root of a signed floating point
     * @notice only positive numbers can have their square root calculated through this function
     * @param a the numerator to get the square root of
     * @return r the result of √a
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a < b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a less than or equals to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a <= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a > b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs a greater than or equal to comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a >= b
     */
  - Float128.sol (NatSpec): /**
     * @dev performs an equality comparison
     * @param a the first term
     * @param b the second term
     * @return retVal the result of a == b
     */
  - Float128.sol (NatSpec): /**
     * @dev encodes a pair of signed integer values describing a floating point number into a packedFloat
     * Examples: 1234.567 can be expressed as: 123456 x 10**(-3), or 1234560 x 10**(-4), or 12345600 x 10**(-5), etc.
     * @notice the mantissa can hold a maximum of 38 or 72 digits. Any number in between or more digits will lose precision.
     * @param mantissa the integer that holds the mantissa digits (38 or 72 digits max)
     * @param exponent the exponent of the floating point number (between -8192 and +8191)
     * @return float the encoded number. This value will ocupy a single 256-bit word and will hold the normalized
     * version of the floating-point number (shifts the exponent enough times to have exactly 38 or 72 significant digits)
     */
  - Float128.sol (NatSpec): /**
     * @dev decodes a packedFloat into its mantissa and its exponent
     * @param float the floating-point number expressed as a packedFloat to decode
     * @return mantissa the 38 mantissa digits of the floating-point number
     * @return exponent the exponent of the floating-point number
     */
  - Float128.sol (NatSpec): /// we use 2's complement for mantissa sign
  - Float128.sol (NatSpec): /**
     * @dev finds the amount of digits of a number
     * @param x the number
     * @return log the amount of digits of x
     */
  - Float128.sol: // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Uint512} from "../lib/Uint512.sol";
import {packedFloat} from "./Types.sol";

/**
 * @title Floating point Library base 10 with 38 or 72 digits signed
 * @dev the library uses the type packedFloat which is a uint under the hood
 * @author Inspired by a Python proposal by @miguel-ot and refined/implemented in Solidity by @oscarsernarosero @Palmerg4
 */

library Float128 {
    uint constant MANTISSA_MASK = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    uint constant MANTISSA_SIGN_MASK = 0x1000000000000000000000000000000000000000000000000000000000000;
    uint constant MANTISSA_L_FLAG_MASK = 0x2000000000000000000000000000000000000000000000000000000000000;
    uint constant EXPONENT_MASK = 0xfffc000000000000000000000000000000000000000000000000000000000000;
    uint constant TWO_COMPLEMENT_SIGN_MASK = 0x8000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE = 10;
    uint constant ZERO_OFFSET = 8192;
    uint constant ZERO_OFFSET_MINUS_1 = 8191;
    uint constant EXPONENT_BIT = 242;
    uint constant MAX_DIGITS_M = 38;
    uint constant MAX_DIGITS_M_X_2 = 76;
    uint constant MAX_DIGITS_M_MINUS_1 = 37;
    uint constant MAX_DIGITS_M_PLUS_1 = 39;
    uint constant MAX_DIGITS_L = 72;
    uint constant MAX_DIGITS_L_MINUS_1 = 71;
    uint constant MAX_DIGITS_L_PLUS_1 = 73;
    uint constant DIGIT_DIFF_L_M = 34;
    uint constant DIGIT_DIFF_L_M_PLUS_1 = 35;
    uint constant DIGIT_DIFF_76_L_MINUS_1 = 3;
    uint constant DIGIT_DIFF_76_L = 4;
    uint constant DIGIT_DIFF_76_L_PLUS_1 = 5;
    uint constant MAX_M_DIGIT_NUMBER = 99999999999999999999999999999999999999;
    uint constant MIN_M_DIGIT_NUMBER = 10000000000000000000000000000000000000;
    uint constant MAX_L_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MIN_L_DIGIT_NUMBER = 100000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_L = 1000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF = 10000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIGIT_DIFF_PLUS_1 = 100000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_MINUS_1 = 10000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M = 100000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_PLUS_1 = 1000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_MAX_DIGITS_M_X_2 =
        10000000000000000000000000000000000000000000000000000000000000000000000000000;
    uint constant BASE_TO_THE_DIFF_76_L_MINUS_1 = 1_000;
    uint constant BASE_TO_THE_DIFF_76_L = 10_000;
    uint constant BASE_TO_THE_DIFF_76_L_PLUS_1 = 100_000;
    uint constant MAX_75_DIGIT_NUMBER = 999999999999999999999999999999999999999999999999999999999999999999999999999;
    uint constant MAX_76_DIGIT_NUMBER = 9999999999999999999999999999999999999999999999999999999999999999999999999999;
    int constant MAXIMUM_EXPONENT = -18; // guarantees all results will have at least 18 decimals in the M size. Autoscales to L if necessary

    /**
     * @dev adds 2 signed floating point numbers
     * @param a the first addend
     * @param b the second addend
     * @return r the result of a + b
     */
    function add(packedFloat a, packedFloat b) internal pure returns (packedFloat r) {
        uint addition;
        bool isSubtraction;
        bool sameExponent;
        if (packedFloat.unwrap(a) == 0) return b;
        if (packedFloat.unwrap(b) == 0) return a;
        assembly {
            let aL := gt(and(a, MANTISSA_L_FLAG_MASK), 0)
            let bL := gt(and(b, MANTISSA_L_FLAG_MASK), 0)
            isSubtraction := xor(and(a, MANTISSA_SIGN_MASK), and(b, MANTISSA_SIGN_MASK))
            // we extract the exponent and mantissas for both
            let aExp := and(a, EXPONENT_MASK)
            let bExp := and(b, EXPONENT_MASK)
            let aMan := and(a, MANTISSA_MASK)
            let bMan := and(b, MANTISSA_MASK)
            if iszero(or(aL, bL)) {
                // we add 38 digits of precision in the case of subtraction
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    }
                }
                // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BASE_TO_THE_MAX_DIGITS_M)
                    bMan := mul(bMan, BASE_TO_THE_MAX_DIGITS_M)
                    r := sub(aExp, shl(EXPONENT_BIT, MAX_DIGITS_M))
                    sameExponent := 1
                }
            }
            if or(aL, bL) {
                // we make sure both of them are size L before continuing
                if iszero(aL) {
                    aMan := mul(aMan, BASE_TO_THE_DIGIT_DIFF)
                    aExp := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                if iszero(bL) {
                    bMan := mul(bMan, BASE_TO_THE_DIGIT_DIFF)
                    bExp := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_L_M))
                }
                // we adjust the significant digits and set the exponent of the result
                if gt(aExp, bExp) {
                    r := sub(aExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, bExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        bMan := mul(bMan, exp(BASE, sub(0, adj)))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        bMan := sdiv(bMan, exp(BASE, adj))
                        aMan := mul(aMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                if gt(bExp, aExp) {
                    r := sub(bExp, shl(EXPONENT_BIT, DIGIT_DIFF_76_L))
                    let adj := sub(shr(EXPONENT_BIT, r), shr(EXPONENT_BIT, aExp))
                    let neg := and(TWO_COMPLEMENT_SIGN_MASK, adj)
                    if neg {
                        aMan := mul(aMan, exp(BASE, sub(0, adj)))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                    if iszero(neg) {
                        aMan := sdiv(aMan, exp(BASE, adj))
                        bMan := mul(bMan, BASE_TO_THE_DIFF_76_L)
                    }
                }
                // // if exponents are the same, we don't need to adjust the mantissas. We just set the result's exponent
                if eq(aExp, bExp) {
                    aMan := mul(aMan, BA
  - 2025-04-forte: No docs/ directory (or no .md/.txt/.rst files within it) was found.

_Determined via graph-gated Codex investigation (0 graph queries, 153s)._

## req-R-fuzzing-in-testing::src/Float128.sol: req-R-fuzzing-in-testing::src/Float128.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_add, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_div, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_divL, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_mul, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_sqrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_sub, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testFindNumbeOfDigits, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testGEpackedFloatFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testGTpackedFloatFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLEpackedFloatFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLTpackedFloatFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange0To1, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange1Point2To3, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange1To1Point2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange2ToInfinity, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testToPackedFloatFuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_add_zero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_divL_zero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_div_zero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_mul_zero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_sub_zero

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdStorage.t.sol:testFuzz_Packed2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/lib/forge-std/test/StdUtils.t.sol:testFuzz_RevertIf_BoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_mul: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_div: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_divL: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_add: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_sub: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testEncoded_sqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLEpackedFloatFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLTpackedFloatFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testGTpackedFloatFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testGEpackedFloatFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange1To1Point2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange1Point2To3: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange0To1: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testLnpackedFloatFuzzRange2ToInfinity: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testToPackedFloatFuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/Float128Fuzz.t.sol:testFindNumbeOfDigits: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_mul_zero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_div_zero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_divL_zero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_add_zero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2025-04-forte/test/FloatCommon.sol:testEncoded_sub_zero: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._
