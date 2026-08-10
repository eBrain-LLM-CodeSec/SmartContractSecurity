# Security Audit Report: 2024-08-phi

Findings below were produced by the RTF (Requirement Translation Framework) pipeline: EthTrust requirement routing, deterministic evidence collection, bounded LLM judgment, and (where the bounded judgment was inconclusive, insufficient, or low-confidence) graph-gated Codex investigation.

## req-1-eip155-chainid::src/Cred.sol: req-1-eip155-chainid::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._executeBatchTrade, Cred._handleTrade, Cred.createCred, Cred.updateCred

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Cred.createCred: keccak256() call at node 1: block.chainid is NOT read in the same expression -- whether this is a transaction/signature-authorization hash at all is NOT determined here (blocked applicability component, see this requirement's own L5 record)
  - Cred.updateCred: keccak256() call at node 1: block.chainid is NOT read in the same expression -- whether this is a transaction/signature-authorization hash at all is NOT determined here (blocked applicability component, see this requirement's own L5 record)
  - Cred._handleTrade: keccak256() call at node 48: block.chainid is NOT read in the same expression -- whether this is a transaction/signature-authorization hash at all is NOT determined here (blocked applicability component, see this requirement's own L5 record)
  - Cred._executeBatchTrade: keccak256() call at node 27: block.chainid is NOT read in the same expression -- whether this is a transaction/signature-authorization hash at all is NOT determined here (blocked applicability component, see this requirement's own L5 record)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-1-no-assembly::src/Cred.sol: req-1-no-assembly::src/Cred.sol

**Requirement:** 

**Location(s):** Address._revert, Cred._getCuratorData, Cred.getPositionsForCurator, ECDSA.emptySignature, ECDSA.recover, ECDSA.recoverCalldata, ECDSA.toEthSignedMessageHash, ECDSA.tryRecover, ECDSA.tryRecoverCalldata, EnumerableMap.keys, EnumerableSet.values, Initializable._getInitializableStorage, LibString.concat, LibString.directReturn, LibString.endsWith, LibString.eq, LibString.eqs, LibString.escapeHTML, LibString.escapeJSON, LibString.fromSmallString, LibString.indexOf, LibString.indicesOf, LibString.is7BitASCII, LibString.lastIndexOf, LibString.normalizeSmallString, LibString.packOne, LibString.packTwo, LibString.repeat, LibString.replace, LibString.runeCount, LibString.slice, LibString.split, LibString.startsWith, LibString.toCase, LibString.toHexString, LibString.toHexStringChecksummed, LibString.toHexStringNoPrefix, LibString.toMinimalHexString, LibString.toMinimalHexStringNoPrefix, LibString.toSmallString, LibString.toString, LibString.unpackOne, LibString.unpackTwo, Ownable2StepUpgradeable._getOwnable2StepStorage, OwnableUpgradeable._getOwnableStorage, PausableUpgradeable._getPausableStorage, SafeTransferLib.balanceOf, SafeTransferLib.forceSafeTransferAllETH, SafeTransferLib.forceSafeTransferETH, SafeTransferLib.safeApprove, SafeTransferLib.safeApproveWithRetry, SafeTransferLib.safeTransfer, SafeTransferLib.safeTransferAll, SafeTransferLib.safeTransferAllETH, SafeTransferLib.safeTransferAllFrom, SafeTransferLib.safeTransferETH, SafeTransferLib.safeTransferFrom, SafeTransferLib.trySafeTransferAllETH, SafeTransferLib.trySafeTransferETH, StorageSlot.getAddressSlot, StorageSlot.getBooleanSlot, StorageSlot.getBytes32Slot, StorageSlot.getBytesSlot, StorageSlot.getStringSlot, StorageSlot.getUint256Slot

**Confidence:** HIGH

**Mechanism:** Inline assembly is present in Cred.getPositionsForCurator and Cred._getCuratorData to resize arrays. No accompanying documentation or stated overriding requirements are found. Because assembly is used without meeting the allowed overriding conditions, the requirement is violated.

**Supporting evidence:**
  - SafeTransferLib.trySafeTransferAllETH: SafeTransferLib.trySafeTransferAllETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#159-167) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#164-166)
  - LibString.repeat: LibString.repeat(string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#665-695) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#671-694)
  - SafeTransferLib.forceSafeTransferETH: SafeTransferLib.forceSafeTransferETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#117-131) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#119-130)
  - LibString.toSmallString: LibString.toSmallString(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#944-954) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#946-953)
  - ECDSA.recover: ECDSA.recover(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#38-79) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#40-78)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#206-247) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#212-246)
  - LibString.toCase: LibString.toCase(string,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#888-914) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#894-913)
  - LibString.unpackTwo: LibString.unpackTwo(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1155-1177) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1161-1176)
  - ECDSA.tryRecoverCalldata: ECDSA.tryRecoverCalldata(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#250-291) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#256-290)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#214-248) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#216-247)
  - LibString.toString: LibString.toString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#36-71) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#38-70)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.UintToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#240-250) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#245-247)
  - LibString.eq: LibString.eq(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1068-1073) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1070-1072)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,uint8,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#326-353) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#332-352)
  - LibString.split: LibString.split(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#801-846) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#808-845)
  - ECDSA.recover: ECDSA.recover(bytes32,uint8,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#162-193) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#168-192)
  - Cred._getCuratorData: Cred._getCuratorData(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#897-935) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#930-932)
  - SafeTransferLib.safeTransferAllFrom: SafeTransferLib.safeTransferAllFrom(address,address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#206-241) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#211-240)
  - SafeTransferLib.forceSafeTransferAllETH: SafeTransferLib.forceSafeTransferAllETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#104-114) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#106-113)
  - LibString.toHexString: LibString.toHexString(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#101-110) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#104-109)
  - ECDSA.toEthSignedMessageHash: ECDSA.toEthSignedMessageHash(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#377-398) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#379-397)
  - LibString.toString: LibString.toString(int256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#74-90) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#82-89)
  - SafeTransferLib.trySafeTransferETH: SafeTransferLib.trySafeTransferETH(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#148-156) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#153-155)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.AddressSet) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#293-303) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#298-300)
  - LibString.startsWith: LibString.startsWith(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#616-634) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#622-633)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#295-322) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#301-321)
  - LibString.lastIndexOf: LibString.lastIndexOf(string,string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#565-597) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#571-596)
  - LibString.indicesOf: LibString.indicesOf(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#742-798) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#748-797)
  - LibString.indexOf: LibString.indexOf(string,string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#496-549) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#502-548)
  - LibString.toMinimalHexString: LibString.toMinimalHexString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#184-194) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#187-193)
  - SafeTransferLib.forceSafeTransferAllETH: SafeTransferLib.forceSafeTransferAllETH(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#134-145) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#136-144)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#117-163) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#123-162)
  - LibString.toHexString: LibString.toHexString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#169-178) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#172-177)
  - LibString.toHexStringChecksummed: LibString.toHexStringChecksummed(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#254-271) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#257-270)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.UintToAddressMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#334-344) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#339-341)
  - StorageSlot.getStringSlot: StorageSlot.getStringSlot(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#109-114) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#111-113)
  - Cred.getPositionsForCurator: Cred.getPositionsForCurator(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#480-523) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#519-522)
  - LibString.directReturn: LibString.directReturn(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1180-1193) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1181-1192)
  - SafeTransferLib.safeTransferETH: SafeTransferLib.safeTransferETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#64-72) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#66-71)
  - LibString.escapeHTML: LibString.escapeHTML(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#969-999) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#971-998)
  - SafeTransferLib.forceSafeTransferETH: SafeTransferLib.forceSafeTransferETH(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#87-101) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#89-100)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.Bytes32Set) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#219-229) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#224-226)
  - LibString.toMinimalHexStringNoPrefix: LibString.toMinimalHexStringNoPrefix(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#199-208) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#202-207)
  - StorageSlot.getBytes32Slot: StorageSlot.getBytes32Slot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#79-84) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#81-83)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.Bytes32ToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#522-532) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#527-529)
  - ECDSA.toEthSignedMessageHash: ECDSA.toEthSignedMessageHash(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#363-370) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#365-369)
  - LibString.slice: LibString.slice(string,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#699-728) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#705-727)
  - Address._revert: Address._revert(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/Address.sol#146-158) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/Address.sol#151-154)
  - SafeTransferLib.safeApprove: SafeTransferLib.safeApprove(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#301-319) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#303-318)
  - LibString.fromSmallString: LibString.fromSmallString(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#918-930) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#920-929)
  - SafeTransferLib.safeTransferAllETH: SafeTransferLib.safeTransferAllETH(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#75-84) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#77-83)
  - LibString.eqs: LibString.eqs(string,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1076-1091) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1078-1090)
  - StorageSlot.getAddressSlot: StorageSlot.getAddressSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#59-64) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#61-63)
  - StorageSlot.getUint256Slot: StorageSlot.getUint256Slot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#89-94) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#91-93)
  - LibString.packOne: LibString.packOne(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1095-1109) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1097-1108)
  - LibString.is7BitASCII: LibString.is7BitASCII(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#385-407) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#387-406)
  - Initializable._getInitializableStorage: Initializable._getInitializableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol#223-227) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol#224-226)
  - StorageSlot.getBytesSlot: StorageSlot.getBytesSlot(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#129-134) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#131-133)
  - LibString.endsWith: LibString.endsWith(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#637-662) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#643-661)
  - LibString.toHexString: LibString.toHexString(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#275-284) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#278-283)
  - LibString.runeCount: LibString.runeCount(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#367-381) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#369-380)
  - LibString.concat: LibString.concat(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#850-884) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#856-883)
  - StorageSlot.getBytesSlot: StorageSlot.getBytesSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#119-124) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#121-123)
  - OwnableUpgradeable._getOwnableStorage: OwnableUpgradeable._getOwnableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol#30-34) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol#31-33)
  - LibString.escapeJSON: LibString.escapeJSON(string,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1003-1060) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1009-1059)
  - SafeTransferLib.safeTransfer: SafeTransferLib.safeTransfer(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#245-263) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#247-262)
  - ECDSA.emptySignature: ECDSA.emptySignature() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#405-410) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#407-409)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#338-360) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#340-359)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#288-321) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#290-320)
  - LibString.packTwo: LibString.packTwo(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1132-1150) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1134-1149)
  - StorageSlot.getStringSlot: StorageSlot.getStringSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#99-104) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#101-103)
  - LibString.unpackOne: LibString.unpackOne(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1114-1128) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1116-1127)
  - SafeTransferLib.safeTransferAll: SafeTransferLib.safeTransferAll(address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#267-297) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#269-296)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.UintSet) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#367-377) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#372-374)
  - LibString.toHexString: LibString.toHexString(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#325-334) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#328-333)
  - PausableUpgradeable._getPausableStorage: PausableUpgradeable._getPausableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol#27-31) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol#28-30)
  - SafeTransferLib.safeApproveWithRetry: SafeTransferLib.safeApproveWithRetry(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#325-355) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#327-354)
  - ECDSA.recoverCalldata: ECDSA.recoverCalldata(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#82-127) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#88-126)
  - SafeTransferLib.balanceOf: SafeTransferLib.balanceOf(address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#359-373) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#361-372)
  - Ownable2StepUpgradeable._getOwnable2StepStorage: Ownable2StepUpgradeable._getOwnable2StepStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol#29-33) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol#30-32)
  - ECDSA.recover: ECDSA.recover(bytes32,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#131-158) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#133-157)
  - LibString.replace: LibString.replace(string,string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#419-491) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#425-490)
  - LibString.normalizeSmallString: LibString.normalizeSmallString(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#933-941) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#935-940)
  - SafeTransferLib.safeTransferFrom: SafeTransferLib.safeTransferFrom(address,address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#178-199) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#180-198)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.AddressToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#428-438) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#433-435)
  - StorageSlot.getBooleanSlot: StorageSlot.getBooleanSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#69-74) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#71-73)

_Determined via graph-gated Codex investigation (0 graph queries, 149s)._

## req-1-use-c-e-i::src/Cred.sol: req-1-use-c-e-i::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._handleTrade, Cred._updateCuratorShareBalance, Cred.createCred

**Confidence:** MEDIUM

**Mechanism:** Single-trade execution performs external ETH transfers and an external deposit without a reentrancy guard and without fully completing effects before interactions (e.g., refund before timestamp updates). Batch trades are guarded, but single trades are not, so the requirement to use CEI or equivalent protection on external calls is violated.

**Supporting evidence:**
  - Cred.createCred: external call at node 21 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 24 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 27 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 34 followed by state write at node 35 (CFG-reachable)
  - Cred._handleTrade: external call at node 13 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 31 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 41 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 45 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 47 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 48 followed by state write at node 50 (CFG-reachable)
  - Cred._updateCuratorShareBalance: external call at node 2 followed by state write at node 6 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 178s)._

## req-1-delegatecall::src/Cred.sol: req-1-delegatecall::src/Cred.sol

**Requirement:** 

**Location(s):** Address.functionDelegateCall

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Address.functionDelegateCall: delegatecall present

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-pass-l1::src/Cred.sol: req-2-pass-l1::src/Cred.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-2-external-calls::src/Cred.sol: req-2-external-calls::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._handleTrade, Cred._updateCuratorShareBalance, Cred.createCred

**Confidence:** MEDIUM

**Mechanism:** The trade handler performs multiple external calls (bonding curve pricing, ETH transfers to user/curator, protocol fee destination, and external rewards contract) to addresses not constrained to the tested set, and it lacks a reentrancy guard in the single-trade path, so protections required by the requirement are not met.

**Supporting evidence:**
  - Cred.createCred: external call at node 21 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 24 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 27 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 34 followed by state write at node 35 (CFG-reachable)
  - Cred._handleTrade: external call at node 13 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 31 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 41 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 45 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 47 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 48 followed by state write at node 50 (CFG-reachable)
  - Cred._updateCuratorShareBalance: external call at node 2 followed by state write at node 6 (CFG-reachable)

_Determined via graph-gated Codex investigation (1 graph queries, 193s)._

## req-2-documented::src/Cred.sol: req-2-documented::src/Cred.sol

**Requirement:** 

**Location(s):** Address._revert, Address.functionCallWithValue, Address.functionDelegateCall, Address.functionStaticCall, Address.sendValue, Cred._createCredInternal, Cred._executeBatchTrade, Cred._getCuratorData, Cred._handleTrade, Cred._recoverSigner, Cred._updateCuratorShareBalance, Cred._validateAndCalculateBatch, Cred.batchBuyShareCred, Cred.batchSellShareCred, Cred.createCred, Cred.getBatchBuyPrice, Cred.getBatchSellPrice, Cred.getCredBuyPrice, Cred.getCredBuyPriceWithFee, Cred.getCredSellPrice, Cred.getCredSellPriceWithFee, Cred.getCuratorAddressLength, Cred.getPositionsForCurator, Cred.getShareNumber, Cred.isShareHolder, Cred.updateCred, ECDSA.emptySignature, ECDSA.recover, ECDSA.recoverCalldata, ECDSA.toEthSignedMessageHash, ECDSA.tryRecover, ECDSA.tryRecoverCalldata, ERC1967Utils._setAdmin, ERC1967Utils._setBeacon, ERC1967Utils._setImplementation, ERC1967Utils.getAdmin, ERC1967Utils.getBeacon, ERC1967Utils.getImplementation, ERC1967Utils.upgradeBeaconToAndCall, ERC1967Utils.upgradeToAndCall, EnumerableMap.at, EnumerableMap.contains, EnumerableMap.keys, EnumerableMap.length, EnumerableMap.remove, EnumerableMap.set, EnumerableSet.values, Initializable._getInitializableStorage, LibString.concat, LibString.directReturn, LibString.endsWith, LibString.eq, LibString.eqs, LibString.escapeHTML, LibString.escapeJSON, LibString.fromSmallString, LibString.indexOf, LibString.indicesOf, LibString.is7BitASCII, LibString.lastIndexOf, LibString.normalizeSmallString, LibString.packOne, LibString.packTwo, LibString.repeat, LibString.replace, LibString.runeCount, LibString.slice, LibString.split, LibString.startsWith, LibString.toCase, LibString.toHexString, LibString.toHexStringChecksummed, LibString.toHexStringNoPrefix, LibString.toMinimalHexString, LibString.toMinimalHexStringNoPrefix, LibString.toSmallString, LibString.toString, LibString.unpackOne, LibString.unpackTwo, Ownable2StepUpgradeable._getOwnable2StepStorage, OwnableUpgradeable._getOwnableStorage, PausableUpgradeable._getPausableStorage, SafeTransferLib.balanceOf, SafeTransferLib.forceSafeTransferAllETH, SafeTransferLib.forceSafeTransferETH, SafeTransferLib.safeApprove, SafeTransferLib.safeApproveWithRetry, SafeTransferLib.safeTransfer, SafeTransferLib.safeTransferAll, SafeTransferLib.safeTransferAllETH, SafeTransferLib.safeTransferAllFrom, SafeTransferLib.safeTransferETH, SafeTransferLib.safeTransferFrom, SafeTransferLib.trySafeTransferAllETH, SafeTransferLib.trySafeTransferETH, StorageSlot.getAddressSlot, StorageSlot.getBooleanSlot, StorageSlot.getBytes32Slot, StorageSlot.getBytesSlot, StorageSlot.getStringSlot, StorageSlot.getUint256Slot, UUPSUpgradeable._checkProxy, UUPSUpgradeable._upgradeToAndCallUUPS

**Confidence:** MEDIUM

**Mechanism:** While the candidate’s assembly use is documented, the requirement mandates documentation for every special-code instance. Multiple block.timestamp usages across Cred.sol lack any explanation of necessity, so the repository does not document all special-code uses.

**Supporting evidence:**
  - SafeTransferLib.trySafeTransferAllETH: SafeTransferLib.trySafeTransferAllETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#159-167) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#164-166)
  - LibString.repeat: LibString.repeat(string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#665-695) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#671-694)
  - SafeTransferLib.forceSafeTransferETH: SafeTransferLib.forceSafeTransferETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#117-131) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#119-130)
  - LibString.toSmallString: LibString.toSmallString(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#944-954) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#946-953)
  - ECDSA.recover: ECDSA.recover(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#38-79) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#40-78)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#206-247) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#212-246)
  - LibString.toCase: LibString.toCase(string,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#888-914) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#894-913)
  - LibString.unpackTwo: LibString.unpackTwo(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1155-1177) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1161-1176)
  - ECDSA.tryRecoverCalldata: ECDSA.tryRecoverCalldata(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#250-291) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#256-290)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#214-248) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#216-247)
  - LibString.toString: LibString.toString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#36-71) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#38-70)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.UintToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#240-250) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#245-247)
  - LibString.eq: LibString.eq(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1068-1073) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1070-1072)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,uint8,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#326-353) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#332-352)
  - LibString.split: LibString.split(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#801-846) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#808-845)
  - ECDSA.recover: ECDSA.recover(bytes32,uint8,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#162-193) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#168-192)
  - Cred._getCuratorData: Cred._getCuratorData(uint256,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#897-935) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#930-932)
  - SafeTransferLib.safeTransferAllFrom: SafeTransferLib.safeTransferAllFrom(address,address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#206-241) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#211-240)
  - SafeTransferLib.forceSafeTransferAllETH: SafeTransferLib.forceSafeTransferAllETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#104-114) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#106-113)
  - LibString.toHexString: LibString.toHexString(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#101-110) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#104-109)
  - ECDSA.toEthSignedMessageHash: ECDSA.toEthSignedMessageHash(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#377-398) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#379-397)
  - LibString.toString: LibString.toString(int256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#74-90) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#82-89)
  - SafeTransferLib.trySafeTransferETH: SafeTransferLib.trySafeTransferETH(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#148-156) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#153-155)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.AddressSet) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#293-303) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#298-300)
  - LibString.startsWith: LibString.startsWith(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#616-634) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#622-633)
  - ECDSA.tryRecover: ECDSA.tryRecover(bytes32,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#295-322) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#301-321)
  - LibString.lastIndexOf: LibString.lastIndexOf(string,string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#565-597) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#571-596)
  - LibString.indicesOf: LibString.indicesOf(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#742-798) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#748-797)
  - LibString.indexOf: LibString.indexOf(string,string,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#496-549) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#502-548)
  - LibString.toMinimalHexString: LibString.toMinimalHexString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#184-194) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#187-193)
  - SafeTransferLib.forceSafeTransferAllETH: SafeTransferLib.forceSafeTransferAllETH(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#134-145) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#136-144)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#117-163) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#123-162)
  - LibString.toHexString: LibString.toHexString(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#169-178) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#172-177)
  - LibString.toHexStringChecksummed: LibString.toHexStringChecksummed(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#254-271) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#257-270)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.UintToAddressMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#334-344) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#339-341)
  - StorageSlot.getStringSlot: StorageSlot.getStringSlot(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#109-114) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#111-113)
  - Cred.getPositionsForCurator: Cred.getPositionsForCurator(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#480-523) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/src/Cred.sol#519-522)
  - LibString.directReturn: LibString.directReturn(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1180-1193) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1181-1192)
  - SafeTransferLib.safeTransferETH: SafeTransferLib.safeTransferETH(address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#64-72) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#66-71)
  - LibString.escapeHTML: LibString.escapeHTML(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#969-999) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#971-998)
  - SafeTransferLib.forceSafeTransferETH: SafeTransferLib.forceSafeTransferETH(address,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#87-101) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#89-100)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.Bytes32Set) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#219-229) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#224-226)
  - LibString.toMinimalHexStringNoPrefix: LibString.toMinimalHexStringNoPrefix(uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#199-208) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#202-207)
  - StorageSlot.getBytes32Slot: StorageSlot.getBytes32Slot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#79-84) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#81-83)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.Bytes32ToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#522-532) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#527-529)
  - ECDSA.toEthSignedMessageHash: ECDSA.toEthSignedMessageHash(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#363-370) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#365-369)
  - LibString.slice: LibString.slice(string,uint256,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#699-728) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#705-727)
  - Address._revert: Address._revert(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/Address.sol#146-158) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/Address.sol#151-154)
  - SafeTransferLib.safeApprove: SafeTransferLib.safeApprove(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#301-319) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#303-318)
  - LibString.fromSmallString: LibString.fromSmallString(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#918-930) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#920-929)
  - SafeTransferLib.safeTransferAllETH: SafeTransferLib.safeTransferAllETH(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#75-84) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#77-83)
  - LibString.eqs: LibString.eqs(string,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1076-1091) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1078-1090)
  - StorageSlot.getAddressSlot: StorageSlot.getAddressSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#59-64) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#61-63)
  - StorageSlot.getUint256Slot: StorageSlot.getUint256Slot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#89-94) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#91-93)
  - LibString.packOne: LibString.packOne(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1095-1109) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1097-1108)
  - LibString.is7BitASCII: LibString.is7BitASCII(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#385-407) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#387-406)
  - Initializable._getInitializableStorage: Initializable._getInitializableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol#223-227) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol#224-226)
  - StorageSlot.getBytesSlot: StorageSlot.getBytesSlot(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#129-134) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#131-133)
  - LibString.endsWith: LibString.endsWith(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#637-662) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#643-661)
  - LibString.toHexString: LibString.toHexString(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#275-284) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#278-283)
  - LibString.runeCount: LibString.runeCount(string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#367-381) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#369-380)
  - LibString.concat: LibString.concat(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#850-884) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#856-883)
  - StorageSlot.getBytesSlot: StorageSlot.getBytesSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#119-124) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#121-123)
  - OwnableUpgradeable._getOwnableStorage: OwnableUpgradeable._getOwnableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol#30-34) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol#31-33)
  - LibString.escapeJSON: LibString.escapeJSON(string,bool) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1003-1060) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1009-1059)
  - SafeTransferLib.safeTransfer: SafeTransferLib.safeTransfer(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#245-263) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#247-262)
  - ECDSA.emptySignature: ECDSA.emptySignature() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#405-410) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#407-409)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#338-360) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#340-359)
  - LibString.toHexStringNoPrefix: LibString.toHexStringNoPrefix(address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#288-321) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#290-320)
  - LibString.packTwo: LibString.packTwo(string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1132-1150) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1134-1149)
  - StorageSlot.getStringSlot: StorageSlot.getStringSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#99-104) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#101-103)
  - LibString.unpackOne: LibString.unpackOne(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1114-1128) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#1116-1127)
  - SafeTransferLib.safeTransferAll: SafeTransferLib.safeTransferAll(address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#267-297) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#269-296)
  - EnumerableSet.values: EnumerableSet.values(EnumerableSet.UintSet) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#367-377) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableSet.sol#372-374)
  - LibString.toHexString: LibString.toHexString(bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#325-334) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#328-333)
  - PausableUpgradeable._getPausableStorage: PausableUpgradeable._getPausableStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol#27-31) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol#28-30)
  - SafeTransferLib.safeApproveWithRetry: SafeTransferLib.safeApproveWithRetry(address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#325-355) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#327-354)
  - ECDSA.recoverCalldata: ECDSA.recoverCalldata(bytes32,bytes) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#82-127) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#88-126)
  - SafeTransferLib.balanceOf: SafeTransferLib.balanceOf(address,address) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#359-373) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#361-372)
  - Ownable2StepUpgradeable._getOwnable2StepStorage: Ownable2StepUpgradeable._getOwnable2StepStorage() (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol#29-33) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol#30-32)
  - ECDSA.recover: ECDSA.recover(bytes32,bytes32,bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#131-158) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/ECDSA.sol#133-157)
  - LibString.replace: LibString.replace(string,string,string) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#419-491) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#425-490)
  - LibString.normalizeSmallString: LibString.normalizeSmallString(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#933-941) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/LibString.sol#935-940)
  - SafeTransferLib.safeTransferFrom: SafeTransferLib.safeTransferFrom(address,address,address,uint256) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#178-199) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/src/utils/SafeTransferLib.sol#180-198)
  - EnumerableMap.keys: EnumerableMap.keys(EnumerableMap.AddressToUintMap) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#428-438) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/structs/EnumerableMap.sol#433-435)
  - StorageSlot.getBooleanSlot: StorageSlot.getBooleanSlot(bytes32) (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#69-74) uses assembly
	- INLINE ASM (../../../../../.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/utils/StorageSlot.sol#71-73)
  - UUPSUpgradeable._checkProxy: makes an external call
  - UUPSUpgradeable._upgradeToAndCallUUPS: makes an external call
  - UUPSUpgradeable._upgradeToAndCallUUPS: makes an external call
  - ERC1967Utils.getImplementation: makes an external call
  - ERC1967Utils._setImplementation: makes an external call
  - ERC1967Utils.upgradeToAndCall: makes an external call
  - ERC1967Utils.getAdmin: makes an external call
  - ERC1967Utils._setAdmin: makes an external call
  - ERC1967Utils.getBeacon: makes an external call
  - ERC1967Utils._setBeacon: makes an external call
  - ERC1967Utils._setBeacon: makes an external call
  - ERC1967Utils.upgradeBeaconToAndCall: makes an external call
  - Address.sendValue: makes an external call
  - Address.functionCallWithValue: makes an external call
  - Address.functionStaticCall: makes an external call
  - Address.functionDelegateCall: makes an external call
  - EnumerableMap.set: makes an external call
  - EnumerableMap.remove: makes an external call
  - EnumerableMap.contains: makes an external call
  - EnumerableMap.length: makes an external call
  - EnumerableMap.at: makes an external call
  - EnumerableMap.keys: makes an external call
  - Cred.batchBuyShareCred: makes an external call
  - Cred.batchSellShareCred: makes an external call
  - Cred.createCred: makes an external call
  - Cred.createCred: makes an external call
  - Cred.createCred: makes an external call
  - Cred.createCred: makes an external call
  - Cred.getCredBuyPrice: makes an external call
  - Cred.getCredSellPrice: makes an external call
  - Cred.getCredBuyPriceWithFee: makes an external call
  - Cred.getCredSellPriceWithFee: makes an external call
  - Cred.getBatchBuyPrice: makes an external call
  - Cred.getBatchSellPrice: makes an external call
  - Cred.isShareHolder: makes an external call
  - Cred.getShareNumber: makes an external call
  - Cred.getCuratorAddressLength: makes an external call
  - Cred.getPositionsForCurator: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._handleTrade: makes an external call
  - Cred._updateCuratorShareBalance: makes an external call
  - Cred._updateCuratorShareBalance: makes an external call
  - Cred._updateCuratorShareBalance: makes an external call
  - Cred._executeBatchTrade: makes an external call
  - Cred._executeBatchTrade: makes an external call
  - Cred._validateAndCalculateBatch: makes an external call
  - Cred._validateAndCalculateBatch: makes an external call
  - Cred._recoverSigner: makes an external call
  - Cred._getCuratorData: makes an external call
  - Cred._getCuratorData: makes an external call
  - Cred._getCuratorData: makes an external call
  - Address.functionDelegateCall: delegatecall present
  - Address._revert: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.recoverCalldata: + operation, inside unchecked{} block
  - ECDSA.recoverCalldata: + operation, inside unchecked{} block
  - ECDSA.recoverCalldata: + operation, inside unchecked{} block
  - ECDSA.recover: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.tryRecoverCalldata: + operation, inside unchecked{} block
  - ECDSA.tryRecoverCalldata: + operation, inside unchecked{} block
  - ECDSA.tryRecoverCalldata: + operation, inside unchecked{} block
  - ECDSA.tryRecover: + operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: - operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: + operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: - operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: - operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: + operation, inside unchecked{} block
  - ECDSA.toEthSignedMessageHash: + operation, inside unchecked{} block
  - LibString.toString: + operation, inside unchecked{} block
  - LibString.toString: + operation, inside unchecked{} block
  - LibString.toString: + operation, inside unchecked{} block
  - LibString.toString: + operation, inside unchecked{} block
  - LibString.toString: - operation, inside unchecked{} block
  - LibString.toString: - operation, inside unchecked{} block
  - LibString.toString: - operation, inside unchecked{} block
  - LibString.toString: - operation, inside unchecked{} block
  - LibString.toString: + operation, inside unchecked{} block
  - LibString.toHexString: + operation, inside unchecked{} block
  - LibString.toHexString: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexString: + operation, inside unchecked{} block
  - LibString.toHexString: - operation, inside unchecked{} block
  - LibString.toMinimalHexString: + operation, inside unchecked{} block
  - LibString.toMinimalHexString: + operation, inside unchecked{} block
  - LibString.toMinimalHexString: + operation, inside unchecked{} block
  - LibString.toMinimalHexString: + operation, inside unchecked{} block
  - LibString.toMinimalHexString: - operation, inside unchecked{} block
  - LibString.toMinimalHexString: - operation, inside unchecked{} block
  - LibString.toMinimalHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toMinimalHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toMinimalHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: - operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: + operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: * operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: + operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: * operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: + operation, inside unchecked{} block
  - LibString.toHexStringChecksummed: + operation, inside unchecked{} block
  - LibString.toHexString: + operation, inside unchecked{} block
  - LibString.toHexString: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexString: + operation, inside unchecked{} block
  - LibString.toHexString: - operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.toHexStringNoPrefix: + operation, inside unchecked{} block
  - LibString.runeCount: + operation, inside unchecked{} block
  - LibString.runeCount: + operation, inside unchecked{} block
  - LibString.runeCount: + operation, inside unchecked{} block
  - LibString.runeCount: + operation, inside unchecked{} block
  - LibString.is7BitASCII: + operation, inside unchecked{} block
  - LibString.is7BitASCII: + operation, inside unchecked{} block
  - LibString.is7BitASCII: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: - operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: - operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: - operation, inside unchecked{} block
  - LibString.replace: - operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: - operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.replace: + operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: - operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: - operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: - operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.indexOf: - operation, inside unchecked{} block
  - LibString.indexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: - operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.lastIndexOf: - operation, inside unchecked{} block
  - LibString.lastIndexOf: + operation, inside unchecked{} block
  - LibString.startsWith: + operation, inside unchecked{} block
  - LibString.startsWith: + operation, inside unchecked{} block
  - LibString.endsWith: + operation, inside unchecked{} block
  - LibString.endsWith: - operation, inside unchecked{} block
  - LibString.endsWith: * operation, inside unchecked{} block
  - LibString.endsWith: + operation, inside unchecked{} block
  - LibString.endsWith: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: - operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: - operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.repeat: + operation, inside unchecked{} block
  - LibString.slice: - operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.slice: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: - operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: - operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: - operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.indicesOf: - operation, inside unchecked{} block
  - LibString.indicesOf: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: - operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: + operation, inside unchecked{} block
  - LibString.split: - operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.concat: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.toCase: + operation, inside unchecked{} block
  - LibString.fromSmallString: + operation, inside unchecked{} block
  - LibString.fromSmallString: + operation, inside unchecked{} block
  - LibString.fromSmallString: + operation, inside unchecked{} block
  - LibString.fromSmallString: + operation, inside unchecked{} block
  - LibString.normalizeSmallString: + operation, inside unchecked{} block
  - LibString.toSmallString: + operation, inside unchecked{} block
  - LibString.toSmallString: - operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeHTML: - operation, inside unchecked{} block
  - LibString.escapeHTML: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.escapeJSON: - operation, inside unchecked{} block
  - LibString.escapeJSON: + operation, inside unchecked{} block
  - LibString.eq: + operation, inside unchecked{} block
  - LibString.eq: + operation, inside unchecked{} block
  - LibString.eqs: + operation, inside unchecked{} block
  - LibString.eqs: + operation, inside unchecked{} block
  - LibString.eqs: + operation, inside unchecked{} block
  - LibString.eqs: + operation, inside unchecked{} block
  - LibString.eqs: + operation, inside unchecked{} block
  - LibString.packOne: + operation, inside unchecked{} block
  - LibString.packOne: - operation, inside unchecked{} block
  - LibString.packOne: * operation, inside unchecked{} block
  - LibString.unpackOne: + operation, inside unchecked{} block
  - LibString.unpackOne: + operation, inside unchecked{} block
  - LibString.unpackOne: + operation, inside unchecked{} block
  - LibString.unpackOne: + operation, inside unchecked{} block
  - LibString.packTwo: + operation, inside unchecked{} block
  - LibString.packTwo: - operation, inside unchecked{} block
  - LibString.packTwo: + operation, inside unchecked{} block
  - LibString.packTwo: - operation, inside unchecked{} block
  - LibString.packTwo: + operation, inside unchecked{} block
  - LibString.packTwo: - operation, inside unchecked{} block
  - LibString.packTwo: * operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.unpackTwo: + operation, inside unchecked{} block
  - LibString.directReturn: - operation, inside unchecked{} block
  - LibString.directReturn: + operation, inside unchecked{} block
  - LibString.directReturn: + operation, inside unchecked{} block
  - SafeTransferLib.balanceOf: * operation, inside unchecked{} block
  - Cred.createCred: reads block.timestamp
  - Cred.updateCred: reads block.timestamp
  - Cred.updateCred: reads block.timestamp
  - Cred._createCredInternal: reads block.timestamp
  - Cred._handleTrade: reads block.timestamp
  - Cred._handleTrade: reads block.timestamp
  - Cred._handleTrade: reads block.timestamp
  - Cred._handleTrade: reads block.timestamp
  - Cred._executeBatchTrade: reads block.timestamp
  - Cred._executeBatchTrade: reads block.timestamp
  - Cred._executeBatchTrade: reads block.timestamp
  - Cred._executeBatchTrade: reads block.timestamp

_Determined via graph-gated Codex investigation (1 graph queries, 154s)._

## req-2-check-rounding::src/Cred.sol: req-2-check-rounding::src/Cred.sol

**Requirement:** 

**Location(s):** ECDSA.toEthSignedMessageHash, LibString.eqs, LibString.is7BitASCII, LibString.runeCount, LibString.toHexStringChecksummed, LibString.toString

**Confidence:** MEDIUM

**Mechanism:** Bonding-curve price/fee math relies on truncating division without documenting the error range or reconciling dust. Unlike curator reward distribution, trades do not refund or bound rounding residue, enabling iterative buy/sell cycles to harvest truncated value, violating the requirement to identify, document, and prevent rounding-based value creation.

**Supporting evidence:**
  - ECDSA.toEthSignedMessageHash: division operation (potential rounding)
  - LibString.toString: division operation (potential rounding)
  - LibString.toHexStringChecksummed: division operation (potential rounding)
  - LibString.runeCount: division operation (potential rounding)
  - LibString.is7BitASCII: division operation (potential rounding)
  - LibString.eqs: division operation (potential rounding)

_Determined via graph-gated Codex investigation (1 graph queries, 293s)._

## req-2-malleable-signatures-for-replay::src/Cred.sol: req-2-malleable-signatures-for-replay::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._recoverSigner

**Confidence:** MEDIUM

**Mechanism:** createCred relies on an off-chain signature but lacks any nonce or one-time-use tracking, so the same signedData/signature pair can be replayed to call createCred multiple times before expiry, violating the requirement that signatures used for replay protection cannot be reused.

**Supporting evidence:**
  - Cred._recoverSigner: uses OpenZeppelin ECDSA.recover/tryRecover (malleability-guarded)

_Determined via graph-gated Codex investigation (1 graph queries, 149s)._

## req-3-pass-l2::src/Cred.sol: req-3-pass-l2::src/Cred.sol

**Requirement:** 

**Location(s):** (location not resolved)

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-timelock-for-privileged-actions::src/Cred.sol: req-3-timelock-for-privileged-actions::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** Cred exposes multiple owner-only controls (pause/unpause, fee and address setters, whitelist updates, UUPS upgrade authorization) with no timelock or scheduling; privileged changes execute immediately, violating the requirement for delayed execution of sensitive operations.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (0 graph queries, 191s)._

## req-3-protect-governance::src/Cred.sol: req-3-protect-governance::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** MEDIUM

**Mechanism:** Cred’s governance is centralized in a single owner who can pause, change fee parameters, whitelist curves, set PhiRewards, and upgrade implementation through UUPS with no delay or consensus. The `_authorizeUpgrade` hook only checks `onlyOwner`, offering no takeover resistance; documentation aligns with owner-only upgrades. Absence of timelock/multisig/ voting means governance takeover risk is unmitigated.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 213s)._

## req-3-event-on-state-change::src/Cred.sol: req-3-event-on-state-change::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._addCredIdPerAddress, Cred._removeCredIdPerAddress, Cred._updateCuratorShareBalance, Cred.initialize, Cred.slitherConstructorConstantVariables, Cred.slitherConstructorVariables, ERC1967Utils.slitherConstructorConstantVariables, Initializable._getInitializableStorage, Initializable.slitherConstructorConstantVariables, LibString.slitherConstructorConstantVariables, Ownable2StepUpgradeable._getOwnable2StepStorage, Ownable2StepUpgradeable.slitherConstructorConstantVariables, OwnableUpgradeable._getOwnableStorage, OwnableUpgradeable.slitherConstructorConstantVariables, PausableUpgradeable._getPausableStorage, PausableUpgradeable.slitherConstructorConstantVariables, SafeTransferLib.slitherConstructorConstantVariables, UUPSUpgradeable.slitherConstructorConstantVariables, UUPSUpgradeable.slitherConstructorVariables

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Ownable2StepUpgradeable._getOwnable2StepStorage: writes state but emits no event
  - Ownable2StepUpgradeable.slitherConstructorConstantVariables: writes state but emits no event
  - OwnableUpgradeable._getOwnableStorage: writes state but emits no event
  - OwnableUpgradeable.slitherConstructorConstantVariables: writes state but emits no event
  - Initializable._getInitializableStorage: writes state but emits no event
  - Initializable.slitherConstructorConstantVariables: writes state but emits no event
  - UUPSUpgradeable.slitherConstructorVariables: writes state but emits no event
  - UUPSUpgradeable.slitherConstructorConstantVariables: writes state but emits no event
  - PausableUpgradeable._getPausableStorage: writes state but emits no event
  - PausableUpgradeable.slitherConstructorConstantVariables: writes state but emits no event
  - ERC1967Utils.slitherConstructorConstantVariables: writes state but emits no event
  - LibString.slitherConstructorConstantVariables: writes state but emits no event
  - SafeTransferLib.slitherConstructorConstantVariables: writes state but emits no event
  - Cred.initialize: writes state but emits no event
  - Cred._updateCuratorShareBalance: writes state but emits no event
  - Cred._addCredIdPerAddress: writes state but emits no event
  - Cred._removeCredIdPerAddress: writes state but emits no event
  - Cred.slitherConstructorVariables: writes state but emits no event
  - Cred.slitherConstructorConstantVariables: writes state but emits no event

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-intended-replay::src/Cred.sol: req-3-intended-replay::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** createCred accepts a phi-signed payload verified only by signer address and expiry; there is no nonce or used-signature registry, and the payload lacks a unique identifier. The same signature can be replayed multiple times to create multiple new credentials. Reuse is neither prevented nor documented as intended or safe, violating the intended-replay requirement.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 303s)._

## req-3-document-system::src/Cred.sol: req-3-document-system::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** MEDIUM

**Mechanism:** Architecture and usage are documented in docs/overview.md with roles listed in docs/users.md, but there is no documentation of security assumptions or privileged on-chain roles (ownership/upgrade authority). Requirement demands coverage of design, privileged roles, security assumptions, and intended usage; missing security assumptions and clear privileged role documentation results in non-compliance.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 150s)._

## req-3-document-threats::src/Cred.sol: req-3-document-threats::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** Repository documentation and source files reviewed show no threat model or security assumptions. Searches for threat/risk/security-related documentation returned nothing. Requirement for documented threat models is unmet.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 272s)._

## req-3-annotate::src/Cred.sol: req-3-annotate::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._addCredIdPerAddress, Cred._removeCredIdPerAddress, Cred.batchBuyShareCred, Cred.batchSellShareCred, Cred.buyShareCred, Cred.buyShareCredFor, Cred.getCreatorRoyalty, Cred.getCredBuyPriceWithFee, Cred.getCredCreator, Cred.getCredSellPrice, Cred.getCredSellPriceWithFee, Cred.getCuratorAddressLength, Cred.getCurrentSupply, Cred.sellShareCred, Cred.version, IBondingCurve.getPriceData

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - Cred.version: public/external function has no NatSpec annotation
  - Cred.buyShareCred: public/external function has no NatSpec annotation
  - Cred.sellShareCred: public/external function has no NatSpec annotation
  - Cred.buyShareCredFor: public/external function has no NatSpec annotation
  - Cred.batchBuyShareCred: public/external function has no NatSpec annotation
  - Cred.batchSellShareCred: public/external function has no NatSpec annotation
  - Cred.getCredSellPrice: public/external function has no NatSpec annotation
  - Cred.getCredBuyPriceWithFee: public/external function has no NatSpec annotation
  - Cred.getCredSellPriceWithFee: public/external function has no NatSpec annotation
  - Cred.getCredCreator: public/external function has no NatSpec annotation
  - Cred.getCurrentSupply: public/external function has no NatSpec annotation
  - Cred.getCreatorRoyalty: public/external function has no NatSpec annotation
  - Cred.getCuratorAddressLength: public/external function has no NatSpec annotation
  - Cred._addCredIdPerAddress: public/external function has no NatSpec annotation
  - Cred._removeCredIdPerAddress: public/external function has no NatSpec annotation
  - IBondingCurve.getPriceData: public/external function has no NatSpec annotation

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-3-implement-as-documented::src/Cred.sol: req-3-implement-as-documented::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** Documentation promises direct royalty delivery and a fixed 5% protocol share fee. Implementation instead routes royalties into a rewards contract balance requiring withdrawal and uses a configurable protocol fee. These behavioral mismatches mean the tested code does not implement the documented logic.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 378s)._

## req-3-access-control::src/Cred.sol: req-3-access-control::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._addCredIdPerAddress, Cred._removeCredIdPerAddress, Cred.addToWhitelist, Cred.batchBuyShareCred, Cred.batchSellShareCred, Cred.buyShareCred, Cred.buyShareCredFor, Cred.createCred, Cred.initialize, Cred.pause, Cred.removeFromWhitelist, Cred.sellShareCred, Cred.setPhiRewardsAddress, Cred.setPhiSignerAddress, Cred.setProtocolFeeDestination, Cred.setProtocolFeePercent, Cred.unPause, Cred.updateCred, Ownable2StepUpgradeable.acceptOwnership, Ownable2StepUpgradeable.pendingOwner, Ownable2StepUpgradeable.transferOwnership, OwnableUpgradeable.owner, OwnableUpgradeable.renounceOwnership, OwnableUpgradeable.transferOwnership, PausableUpgradeable.paused

**Confidence:** HIGH

**Mechanism:** Privileged bookkeeping of curator positions is exposed via public functions with no access control, allowing arbitrary external mutation of tracking structures, violating least‑privilege requirements.

**Supporting evidence:**
  - Ownable2StepUpgradeable.pendingOwner: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Ownable2StepUpgradeable.transferOwnership: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Ownable2StepUpgradeable.acceptOwnership: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - OwnableUpgradeable.owner: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - OwnableUpgradeable.renounceOwnership: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - OwnableUpgradeable.transferOwnership: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - PausableUpgradeable.paused: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.initialize: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.pause: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.unPause: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.setPhiSignerAddress: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.setProtocolFeeDestination: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.setProtocolFeePercent: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.setPhiRewardsAddress: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.addToWhitelist: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.removeFromWhitelist: state-mutating function is PROTECTED (access-controlled) per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.buyShareCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.sellShareCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.buyShareCredFor: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.batchBuyShareCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.batchSellShareCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.createCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred.updateCred: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred._addCredIdPerAddress: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here
  - Cred._removeCredIdPerAddress: state-mutating function is UNPROTECTED -- callable by anyone per Slither's own is_protected() heuristic -- evidence only, whether the granted access level is the MINIMUM necessary needs a documentation cross-check, not attempted here

_Determined via graph-gated Codex investigation (1 graph queries, 124s)._

## req-3-no-single-admin-eoa::src/Cred.sol: req-3-no-single-admin-eoa::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** Cred relies on Ownable2StepUpgradeable, setting a single owner in initialization. All critical admin actions, including pausing, fee/signer/rewards/whitelist setters, and upgrades, are gated by onlyOwner with no multisig or higher-privileged multisig admin. No multisig/timelock exists elsewhere, so critical operations can be performed by a single EOA, violating the requirement.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 151s)._

## req-3-external-calls::src/Cred.sol: req-3-external-calls::src/Cred.sol

**Requirement:** 

**Location(s):** Cred._handleTrade, Cred._updateCuratorShareBalance, Cred.createCred

**Confidence:** MEDIUM

**Mechanism:** _handleTrade performs multiple external value-transferring calls to arbitrary users and external contracts without a reentrancy guard, and the function lacks documentation describing the external interactions or protections. Requirement for documented and protected external calls is therefore not met.

**Supporting evidence:**
  - Cred.createCred: external call at node 21 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 24 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 27 followed by state write at node 35 (CFG-reachable)
  - Cred.createCred: external call at node 34 followed by state write at node 35 (CFG-reachable)
  - Cred._handleTrade: external call at node 13 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 31 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 41 followed by state write at node 43 (CFG-reachable)
  - Cred._handleTrade: external call at node 45 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 47 followed by state write at node 50 (CFG-reachable)
  - Cred._handleTrade: external call at node 48 followed by state write at node 50 (CFG-reachable)
  - Cred._updateCuratorShareBalance: external call at node 2 followed by state write at node 6 (CFG-reachable)

_Determined via graph-gated Codex investigation (0 graph queries, 132s)._

## req-3-consistent-solidity-output::src/Cred.sol: req-3-consistent-solidity-output::src/Cred.sol

**Requirement:** 

**Location(s):** pragma solidity^0.8.20, pragma solidity^0.8.4

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.20: pragma '^0.8.20' is a range, not an exact pin
  - pragma solidity^0.8.4: pragma '^0.8.4' is a range, not an exact pin
  - pragma solidity^0.8.4: pragma '^0.8.4' is a range, not an exact pin
  - pragma solidity^0.8.4: pragma '^0.8.4' is a range, not an exact pin

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-check-new-bugs::src/Cred.sol: req-R-check-new-bugs::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** MEDIUM

**Mechanism:** Searched README and docs; no references to checking solidity-bugs-json or addressing compiler vulnerabilities after Nov 2023. Build config pins solc 0.8.25 with no documented review of newer bugs. Requirement to check for and address new compiler bugs is not evidenced.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 276s)._

## req-R-use-latest-compiler::src/Cred.sol: req-R-use-latest-compiler::src/Cred.sol

**Requirement:** 

**Location(s):** compiler config

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - compiler config: solc 0.8.25 != caller-supplied latest known stable version 0.8.36 (external, time-anchored reference -- not derived from spec text)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-notify-news::src/Cred.sol: req-R-notify-news::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** MEDIUM

**Mechanism:** Requirement asks for responsible disclosure guidance. Project documentation (README.md and docs/) provides general security bullet points but no instructions on reporting new vulnerabilities or contacting maintainers, and code contains no NatSpec security-contact tags. Searches across repo found only third-party OpenZeppelin SECURITY.md, not project policy. Thus repository lacks required responsible disclosure guidance.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 245s)._

## req-R-fuzzing-in-testing::src/Cred.sol: req-R-fuzzing-in-testing::src/Cred.sol

**Requirement:** 

**Location(s):** /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_Bound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_BoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_Bound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_BoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdChains.t.sol:testRpc, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol:testRpc, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/governance/Governor.t.sol:testInvalidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/governance/Governor.t.sol:testValidDescriptionForProposer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testLengthShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testLengthWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRevertLong, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRoundtripShort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRoundtripWithFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testCeilDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog10, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testMulDivDomain, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testSqrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testLookup, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testPush, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AsserNottEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_IntErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_IntErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Int_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Int_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_UintErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_UintErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Uint_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Uint_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BoolErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BoolErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bool_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bool_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BytesErr_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArrErr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArrErr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_FailEl, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_FailLen, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_BytesErr_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_Bytes_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_Bytes_Pass, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdChains.t.sol:testFuzz_Rpc, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_Bound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_BoundInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeDecode, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeDecodeAltModes, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeFileSafeAndNoPadding, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDeployERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDoubleDeployDifferentBytecodeReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDoubleDeploySameBytecodeReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffDays, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffHours, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffMinutes, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffMonths, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffSeconds, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffYears, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateTimeToAndFroTimestamp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToAndFroEpochDay, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToEpochDayDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToEpochDayDifferential2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDaysInMonth, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDate, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDateDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDateDifferential2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsLeapYear, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsSupportedDateTime, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsWeekEnd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testMondayTimestamp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testNthWeekdayInMonthOfYearTimestamp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testClear, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testDynamicBuffer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testDynamicBufferReserveFromEmpty3, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ECDSA.t.sol:testRecoverAndTryRecover, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testAuthorizedEquivalence, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBalanceOfBatchWithArrayMismatchReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBalanceOf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurnInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurnWithArrayLengthMismatchReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToERC1155Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToNonERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToRevertingERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToWrongReturnDataERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintWithArrayMismatchReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBurnInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testDirectSetApprovalForAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToERC1155Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToNonERC155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToRevertingERC155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToWrongReturnDataERC155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToERC1155Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToNonERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToRevertingERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToWrongReturnDataERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromWithArrayLengthMismatchReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromSelf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromSelfInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToERC1155Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToNonERC155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToRevertingERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToWrongReturnDataERC1155RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployAndCall, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployBrutalized, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployDeterministicAndCall, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testBurnInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testDirectSpendAllowance, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testDirectTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitBadDeadlineReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitBadNonceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitPastDeadlineReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitReplayReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFromInsufficientAllowanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFromInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC2981.t.sol:testRoyaltyOverflowCheckDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC2981.t.sol:testSetAndGetRoyaltyInfo, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337.t.sol:testDelegateExecute, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337.t.sol:testExecuteBatch, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337Factory.t.sol:testCreateAccountRepeatedDeployment, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337Factory.t.sol:testDeployDeterministic, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testDifferentialFullMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testSingleDepositWithdraw, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testSingleMintRedeem, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testDeployERC6551, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testExecuteBatch, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testOnERC721ReceivedCyclesWithDifferentChainIds, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testBurnInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testDirectFunctions, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMetadata, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMintOverMaxUintReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testSetOperator, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransfer, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromCallerIsNotOperator, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromInsufficientAllowanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromOverMaxUintReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferInsufficientBalanceReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferOverMaxUintReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApprove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveNonExistentReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveUnauthorizedReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testAuthorizedEquivalence, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testAux, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testBurn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testBurnNonExistentReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testDoubleBurnReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testDoubleMintReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testEverything, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testExtraData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testExtraData2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testIsApprovedOrOwner, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testMint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testMintToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testOwnerOfNonExistent, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithWrongReturnData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithWrongReturnDataWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToNonERC721RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToNonERC721RecipientWithDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToRevertingERC721RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToRevertingERC721RecipientWithDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToEOA, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721Recipient, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithData, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithWrongReturnDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithWrongReturnDataWithDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToNonERC721RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToNonERC721RecipientWithDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToRevertingERC721RecipientReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToRevertingERC721RecipientWithDataReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafetyOfCustomStorage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFrom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromApproveAll, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromNotExistentReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromNotOwner, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromSelf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromToZeroReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromWrongFromReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testAbs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrtBack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrtWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testClamp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testClampSigned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDist, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUpOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUpZeroDenominatorReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadZeroDenominatorReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testFullMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testFullMulDivUp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testGcd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadAccuracy, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasing, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasingAround, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasingAround2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadWithinBounds, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog10, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog2Differential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMax, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMaxCasted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMaxSigned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMin, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMinBrutalized, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMinSigned, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUpOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUpZeroDenominatorReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivZeroDenominatorReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadUp, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadUpOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testPackUnpackSci, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawAdd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawAddMod, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMod, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMul, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMulMod, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSDiv, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSMod, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSub, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWadOverflowReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWadZeroDenominatorReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowRevertsOnCondition1, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowRevertsOnCondition2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowTrickDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSci, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSci2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtBack, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtHashed, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtWad, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testZeroFloorSub, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testZeroFloorSubCasted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testDecodeEncodedStringDoesNotRevert, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testParseUint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testParseValidObjectDoesNotRevert, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testAnd, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testAutoClean, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testBoolToUint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testIsPo2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testOr, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testPopCount, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testReverseBitsDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testReverseBytesDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapFindLastSet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapPopCount, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSetTo, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapToggle, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapUnset, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testClone, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneDeteministicWithImmutableArgs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneDeterministic, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneWithImmutableArgs, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testDeployDeterministicERC1967, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testDeployERC1967, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testStartsWith, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testFoundStatementDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testGeneralMapFunctionsWithSmallBitWidths, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testGeneralMapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32Maps, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSearchSorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSetAndGet, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSetAndGet2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibRLP.t.sol:testComputeAddressDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testInsertionSortAddressesDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testInsertionSortPsuedorandom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAddressesDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedAddressesDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedIntsDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedIntsDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedElementInArray, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedElementNotInArray, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedInts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortAddressesDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortAddressesPsuedorandom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortChecksumed, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortOriginalPsuedorandom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortPsuedorandom, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortPsuedorandomNonuniform, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceDifferentialInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceUnionIntersection, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedIntersectionDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedIntersectionDifferentialInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedUnionDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedUnionDifferentialInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testTwoComplementConversionSort, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySorted, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySortedAddress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySortedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testAddressToHexStringZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testBytesToHexString, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testBytesToHexStringNoPrefix, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testFromAddressToHexStringChecksummedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testHexStringNoPrefixVariants, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testNormalizeSmallString, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringConcat, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringDirectReturn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEndsWith, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEq, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEscapeHTML, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIndexOf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIndicesOf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIs7BitASCIIDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringLastIndexOf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringLowerDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackOne, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackOneDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackTwo, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackTwoDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringRepeat, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringReplace, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringRuneCountDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringSlice, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringSplit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringStartsWith, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringUpperDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToHexStringFixedLengthZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToHexStringZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToMinimalHexStringNoPrefixZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToMinimalHexStringZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringSignedDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringSignedMemory, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringZeroRightPadded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdCompressDecompress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallback, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallbackDecompressor, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallbackMaskTrick, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testDecompressWontRevert, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testFlzCompressDecompress, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProof, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForHeightOneTree, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForHeightTwoTree, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForSingleLeaf, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProof, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProofBasicCase, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProofForHeightOneTree, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testBoundsCheckDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadString, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadStringTruncated, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadUint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapEnqueue, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapEnqueueGas, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapPushAndPop, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapPushPop, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapReplace, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapRoot, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Multicallable.t.sol:testMulticallableReturnDataIsProperlyEncoded, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Multicallable.t.sol:testMulticallableRevertWithMessage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testHandoverOwnership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testOnlyOwnerModifier, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testSetOwnerDirect, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testTransferOwnership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testGrantAndRemoveRolesDirect, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testGrantAndRevokeOrRenounceRoles, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHandoverOwnership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHasAllRoles, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHasAnyRole, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyOwnerModifier, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyOwnerOrRolesModifier, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyRolesModifier, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyRolesOrOwnerModifier, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOrdinalsFromRoles, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testRolesFromOrdinals, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testSetOwnerDirect, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testSetRolesDirect, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testTransferOwnership, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeClear, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeInsertAndRemove, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeInsertAndRemove2, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearest, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearestAfter, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearestBefore, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerCustomBoundsReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerCustomStartBoundReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerRevert, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteRead, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomBounds, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomBoundsOutOfRangeReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomStartBound, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomStartBoundOutOfRangeReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadDeterministic, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToInt, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToInt256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToUint, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToUint256, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithGarbageReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithMissingReturn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithNonContract, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithNonGarbage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRetry, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRetryWithNonContract, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsFalseReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTooLittleReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTooMuch, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTwoReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRevertingReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testBalanceOfStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testForceTransferETHToGriever, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllETH, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllETHToContractWithoutFallbackReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllFromWithStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllWithStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferETH, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferETHToContractWithoutFallbackReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithGarbageReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithMissingReturn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithNonContract, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithNonGarbage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsFalseReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTooLittleReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTooMuch, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTwoReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithRevertingReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithGarbageReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithMissingReturn, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithNonContract, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithNonGarbage, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsFalseReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTooLittleReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTooMuch, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTwoReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithRevertingReverts, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithStandardERC20, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SignatureCheckerLib.t.sol:testSignatureChecker, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SignatureCheckerLib.t.sol:testToEthSignedMessageHashDifferential, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testDeposit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testFallbackDeposit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testWithdraw, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/test/RewardControl.t.sol:testDeposit, /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/test/RewardControl.t.sol:testDepositBatch

**Confidence:** unknown

**Mechanism:** (no reasoning summary returned)

**Supporting evidence:**
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageCheckedWriteMapPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzz_StorageNativePack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdStorage.t.sol:testFuzzPacked2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testPermit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailBurnInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientAllowance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailTransferFromInsufficientBalance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadNonce: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitBadDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitPastDeadline: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC20.t.sol:testFailPermitReplay: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testTransferFromApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeTransferFromToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testSafeMintToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailMintToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailBurnUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailDoubleBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnMinted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailApproveUnAuthorized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromUnOwned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromWrongFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromToZero: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailTransferFromNotOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeTransferFromToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToNonERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToRevertingERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailSafeMintToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/foundry-devops/lib/forge-std/test/mocks/MockERC721.t.sol:testFailOwnerOfUnminted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdChains.t.sol:testRpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testBoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdChains.t.sol:testRpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdCheats.t.sol:testAssumeNoPrecompiles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetAbs_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Uint_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdMath.t.sol:testGetPercentDelta_Int_Fuzz: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testBoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/lib/forge-std/test/StdUtils.t.sol:testCannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testValidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/governance/Governor.t.sol:testInvalidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRoundtripWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testRevertLong: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/ShortStrings.t.sol:testLengthWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testCeilDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/math/Math.t.sol:testMulDivDomain: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/governance/Governor.t.sol:testValidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/governance/Governor.t.sol:testInvalidDescriptionForProposer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/metatx/ERC2771Forwarder.t.sol:testExecuteAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/metatx/ERC2771Forwarder.t.sol:testExecuteBatchAvoidsETHStuck: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC20/extensions/ERC4626.t.sol:testFuzzDecimalsOverflow: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_balance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_ownership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_burn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_transfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/token/ERC721/extensions/ERC721Consecutive.t.sol:test_start_consecutive_id: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRoundtripShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRoundtripWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testRevertLong: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testLengthShort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/ShortStrings.t.sol:testLengthWithFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testCeilDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/math/Math.t.sol:testMulDivDomain: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testPush: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-contracts-upgradeable/test/utils/structs/Checkpoints.t.sol:testLookup: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bool_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bool_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BoolErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BoolErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArrErr_FailEl: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_UintArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_IntArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEq_AddressArrErr_FailLen: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbs_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqAbsDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_Uint_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_Uint_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_UintErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRelDecimal_UintErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertApproxEqRel_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_Int_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testAssertApproxEqRelDecimal_IntErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Return_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Return_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertEqCall_Revert_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Revert_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_RevertWhenCalled_AssertEqCall_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_Bytes_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_Bytes_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AssertNotEq_BytesErr_Pass: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdAssertions.t.sol:testFuzz_AsserNottEq_BytesErr_Fail: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdChains.t.sol:testFuzz_Rpc: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeAddressIsNot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotPrecompile: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotForgeAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_TokenWithoutBlacklist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDC: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdCheats.t.sol:testFuzz_AssumeNotBlacklisted_USDT: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Uint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdMath.t.sol:testFuzz_GetPercentDelta_Int: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_Bound_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_Bound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_BoundInt_DistributionIsEven: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_BoundInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/openzeppelin-foundry-upgrades/lib/forge-std/test/StdUtils.t.sol:test_CannotBoundIntMaxLessThanMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeDecode: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeDecodeAltModes: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Base64.t.sol:testBase64EncodeFileSafeAndNoPadding: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDeployERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDoubleDeploySameBytecodeReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/CREATE3.t.sol:testDoubleDeployDifferentBytecodeReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToEpochDayDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToEpochDayDifferential2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDateDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDateDifferential2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testEpochDayToDate: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateToAndFroEpochDay: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDateTimeToAndFroTimestamp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsLeapYear: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testDaysInMonth: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsSupportedDateTime: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testNthWeekdayInMonthOfYearTimestamp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testMondayTimestamp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testIsWeekEnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffYears: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffMonths: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffDays: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffHours: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffMinutes: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DateTimeLib.t.sol:testAddSubDiffSeconds: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testClear: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testDynamicBufferReserveFromEmpty3: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testDynamicBuffer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/DynamicBufferLib.t.sol:testDynamicBuffer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ECDSA.t.sol:testRecoverAndTryRecover: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testDirectSetApprovalForAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testAuthorizedEquivalence: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToERC1155Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToERC1155Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToERC1155Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToERC1155Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBalanceOf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToNonERC155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToRevertingERC155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testMintToWrongReturnDataERC155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBurnInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromSelfInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToNonERC155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToRevertingERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeTransferFromToWrongReturnDataERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToNonERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToRevertingERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromToWrongReturnDataERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testSafeBatchTransferFromWithArrayLengthMismatchReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToNonERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToRevertingERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintToWrongReturnDataERC1155RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchMintWithArrayMismatchReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurnInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBatchBurnWithArrayLengthMismatchReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1155.t.sol:testBalanceOfBatchWithArrayMismatchReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployBrutalized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployAndCall: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC1967Factory.t.sol:testDeployDeterministicAndCall: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testDirectTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testDirectSpendAllowance: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testBurnInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFromInsufficientAllowanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testTransferFromInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitBadNonceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitBadDeadlineReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitPastDeadlineReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC20.t.sol:testPermitReplayReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC2981.t.sol:testRoyaltyOverflowCheckDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC2981.t.sol:testSetAndGetRoyaltyInfo: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337.t.sol:testExecuteBatch: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337.t.sol:testDelegateExecute: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337Factory.t.sol:testDeployDeterministic: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4337Factory.t.sol:testCreateAccountRepeatedDeployment: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testDifferentialFullMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testSingleDepositWithdraw: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC4626.t.sol:testSingleMintRedeem: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testDeployERC6551: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testOnERC721ReceivedCyclesWithDifferentChainIds: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6551.t.sol:testExecuteBatch: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMetadata: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransfer: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testSetOperator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testMintOverMaxUintReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testBurnInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferOverMaxUintReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromOverMaxUintReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromInsufficientAllowanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromInsufficientBalanceReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testTransferFromCallerIsNotOperator: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC6909.t.sol:testDirectFunctions: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafetyOfCustomStorage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testAuthorizedEquivalence: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testMint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testEverything: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testIsApprovedOrOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testExtraData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testExtraData2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testAux: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApprove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveBurn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFrom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromSelf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromApproveAll: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToEOA: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721Recipient: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testMintToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testDoubleMintReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testBurnNonExistentReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testDoubleBurnReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveNonExistentReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testApproveUnauthorizedReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromNotExistentReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromWrongFromReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromToZeroReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testTransferFromNotOwner: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToNonERC721RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToNonERC721RecipientWithDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToRevertingERC721RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToRevertingERC721RecipientWithDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithWrongReturnDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeTransferFromToERC721RecipientWithWrongReturnDataWithDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToNonERC721RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToNonERC721RecipientWithDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToRevertingERC721RecipientReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToRevertingERC721RecipientWithDataReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithWrongReturnData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testSafeMintToERC721RecipientWithWrongReturnDataWithData: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/ERC721.t.sol:testOwnerOfNonExistent: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadAccuracy: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadWithinBounds: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasingAround2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasingAround: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLambertW0WadMonotonicallyIncreasing: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowTrickDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog2Differential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testFullMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testFullMulDivUp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowRevertsOnCondition1: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSMulWadOverflowRevertsOnCondition2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadUp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulWadUpOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWadOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadZeroDenominatorReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSDivWadZeroDenominatorReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUpOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDivWadUpZeroDenominatorReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivZeroDenominatorReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUpOverflowReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMulDivUpZeroDenominatorReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrtWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testCbrtBack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtWad: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtBack: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSqrtHashed: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMin: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMinBrutalized: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMinSigned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMax: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMaxSigned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testMaxCasted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testZeroFloorSub: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testZeroFloorSubCasted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testDist: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testAbs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testGcd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testClamp: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testClampSigned: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawAdd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawAdd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSub: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSub: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMul: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMul: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSDiv: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawSMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawAddMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testRawMulMod: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog10: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testLog256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSci: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testSci2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/FixedPointMathLib.t.sol:testPackUnpackSci: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testParseValidObjectDoesNotRevert: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testDecodeEncodedStringDoesNotRevert: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/JSONParserLib.t.sol:testParseUint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testPopCount: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testIsPo2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testIsPo2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testAnd: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testOr: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testAutoClean: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testBoolToUint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testReverseBitsDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBit.t.sol:testReverseBytesDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapUnset: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSetTo: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapSetTo: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapToggle: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapPopCount: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibBitmap.t.sol:testBitmapFindLastSet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testDeployERC1967: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testClone: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneDeterministic: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testDeployDeterministicERC1967: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneWithImmutableArgs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testCloneDeteministicWithImmutableArgs: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibClone.t.sol:testStartsWith: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSetAndGet: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSetAndGet2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32Maps: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint8MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint16MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint32MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint40MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint64MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testUint128MapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testGeneralMapSearchSorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testGeneralMapFunctionsWithSmallBitWidths: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibMap.t.sol:testFoundStatementDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibRLP.t.sol:testComputeAddressDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testInsertionSortAddressesDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testInsertionSortPsuedorandom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortChecksumed: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortPsuedorandom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortPsuedorandomNonuniform: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortAddressesDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortAddressesPsuedorandom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortOriginalPsuedorandom: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySorted: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySortedAddress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testUniquifySortedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedElementInArray: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedElementNotInArray: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSearchSortedInts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testTwoComplementConversionSort: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedUnionDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedUnionDifferentialInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedIntersectionDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedIntersectionDifferentialInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceDifferentialInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testSortedDifferenceUnionIntersection: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedIntsDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAddressesDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedIntsDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibSort.t.sol:testIsSortedAndUniquifiedAddressesDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringSignedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToStringSignedMemory: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToHexStringZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToHexStringFixedLengthZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testAddressToHexStringZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToMinimalHexStringZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testToMinimalHexStringNoPrefixZeroRightPadded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testFromAddressToHexStringChecksummedDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testHexStringNoPrefixVariants: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testBytesToHexStringNoPrefix: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testBytesToHexString: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIs7BitASCIIDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringRuneCountDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIndexOf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringLastIndexOf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringStartsWith: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEndsWith: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringRepeat: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringSlice: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringIndicesOf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringSplit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringConcat: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEscapeHTML: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringEq: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackOneDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackOne: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackTwoDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringPackAndUnpackTwo: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringDirectReturn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringLowerDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testStringUpperDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibString.t.sol:testNormalizeSmallString: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testFlzCompressDecompress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdCompressDecompress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdCompressDecompress: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallbackDecompressor: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallbackDecompressor: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testDecompressWontRevert: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallback: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/LibZip.t.sol:testCdFallbackMaskTrick: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProofForHeightOneTree: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProof: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyProofBasicCase: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForSingleLeaf: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForHeightOneTree: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProofForHeightTwoTree: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MerkleProofLib.t.sol:testVerifyMultiProof: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadString: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadStringTruncated: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testReadUint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MetadataReaderLib.t.sol:testBoundsCheckDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapRoot: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapPushAndPop: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapPushPop: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapReplace: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapEnqueue: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/MinHeapLib.t.sol:testHeapEnqueueGas: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Multicallable.t.sol:testMulticallableRevertWithMessage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Multicallable.t.sol:testMulticallableReturnDataIsProperlyEncoded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Multicallable.t.sol:testMulticallableReturnDataIsProperlyEncoded: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testSetOwnerDirect: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testTransferOwnership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testOnlyOwnerModifier: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/Ownable.t.sol:testHandoverOwnership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testSetOwnerDirect: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testGrantAndRemoveRolesDirect: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testSetRolesDirect: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testTransferOwnership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testGrantAndRevokeOrRenounceRoles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHasAllRoles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHasAnyRole: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testRolesFromOrdinals: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOrdinalsFromRoles: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyOwnerModifier: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyRolesModifier: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyOwnerOrRolesModifier: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testOnlyRolesOrOwnerModifier: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/OwnableRoles.t.sol:testHandoverOwnership: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeInsertAndRemove: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeInsertAndRemove2: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeClear: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearest: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearestBefore: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/RedBlackTree.t.sol:testRedBlackTreeNearestAfter: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteRead: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomStartBound: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomBounds: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerRevert: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerCustomStartBoundReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testReadInvalidPointerCustomBoundsReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomStartBoundOutOfRangeReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadCustomBoundsOutOfRangeReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SSTORE2.t.sol:testWriteReadDeterministic: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToUint: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToInt: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToInt256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeCastLib.t.sol:testSafeCastToUint256: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testForceTransferETHToGriever: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testBalanceOfStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllWithStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllFromWithStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithMissingReturn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTooMuch: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithNonGarbage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithNonContract: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithMissingReturn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTooMuch: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithNonGarbage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithNonContract: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithMissingReturn: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithStandardERC20: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTooMuch: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithNonGarbage: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithNonContract: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRetryWithNonContract: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRetry: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferETH: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllETH: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsFalseReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithRevertingReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTooLittleReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithReturnsTwoReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferWithGarbageReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsFalseReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithRevertingReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTooLittleReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithReturnsTwoReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferFromWithGarbageReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsFalseReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithRevertingReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTooLittleReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithReturnsTwoReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testApproveWithGarbageReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferETHToContractWithoutFallbackReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SafeTransferLib.t.sol:testTransferAllETHToContractWithoutFallbackReverts: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SignatureCheckerLib.t.sol:testSignatureChecker: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SignatureCheckerLib.t.sol:testToEthSignedMessageHashDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/SignatureCheckerLib.t.sol:testToEthSignedMessageHashDifferential: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testFallbackDeposit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testDeposit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/lib/solady/test/WETH.t.sol:testWithdraw: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/test/RewardControl.t.sol:testDeposit: Foundry-convention parameterized test function (fuzzed by forge test)
  - /scratch/md5344/.claude/jobs/506f33b3/tmp/mgpr_checkouts/2024-08-phi/test/RewardControl.t.sol:testDepositBatch: Foundry-convention parameterized test function (fuzzed by forge test)

_Determined via bounded LLM judgment on deterministically-collected evidence._

## req-R-multisig-threshold::src/Cred.sol: req-R-multisig-threshold::src/Cred.sol

**Requirement:** 

**Location(s):** Cred.sol, Cred.sol (NatSpec), README.md, docs/arweave.md, docs/dev.md, docs/overview.md, docs/users.md

**Confidence:** HIGH

**Mechanism:** Cred’s admin and upgrade controls are single-signer only (Ownable2StepUpgradeable). There is no multisig or threshold enforcement, so privileged actions are effectively 1-of-1, which does not satisfy the recommendation to avoid 1-of-N and to require an appropriate multisig threshold.

**Supporting evidence:**
  - README.md: # Phi audit details

- Total Prize Pool: $30,000 in USDC
  - HM awards: $24,000 in USDC
  - QA awards: $900 in USDC
  - Judge awards: $2,800 in USDC
  - Validator awards: $1,800 USDC
  - Scout awards: $500 in USDC
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts August 22, 2024 20:00 UTC
- Ends September 3, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-08-phi/blob/main/4naly3er-report.md).

_Note for C4 wardens: Anything included in this `Automated Findings / Publicly Known Issues` section is considered a
publicly known issue and is ineligible for awards._

1. updateArtSettings allows setting the startTime to a past timestamp, potentially opening the minting window earlier
   than intended
2. Setting sellRoyalty higher than buyRoyalty may reduce market demand possibly leading to decreased liquidity
3. Lack of upper bound check for mintFee
4. User can claim multiple NFT (not check claimed status)
5. creatorFee to be always zero when supply == 0
6. Solady ECDSA.recover(), which does not reject malleable signature. For this issue, we use expiresIn
7. The credMerkleRoot[credChainId][credId] stores the merkleRootHash, but there is no way to update the merkleRootHash.
8. OZ EnumerableMap is not gas efficiency

# Overview

Phi Protocol is an open credentialing protocol to help users form, visualize, showcase their onchain identity. It
incentivizes individuals to index blockchain transaction data as onchain credential blocks, curate them, host the
verification process, and mint onchain credential contents.

## Links

- **Previous audits:** <https://github.com/code-423n4/2024-08-phi/tree/main/docs/audit>
- **Documentation:** <https://docs.philand.xyz/explore-phi>
- **Website:** <https://phiprotocol.xyz/>
- **X/Twitter:** <https://x.com/phi_xyz>
- **Discord:** <https://discord.gg/phi>

---

## Scoping Q &amp; A

### General questions

| Question                                | Answer                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------- |
| ERC20 used by the protocol              | None                                                                    |
| Test coverage                           | 55% |
| ERC721 used by the protocol             | None                                                                     |
| ERC777 used by the protocol             | None                                                                     |
| ERC1155 used by the protocol            | Any                                                                      |
| Chains the protocol will be deployed on | Base, Optimism, BeraChain, and Other EVM chain                      |

### ERC20 token behaviors in scope

| Question                                                                                                                                                   | Answer   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [Missing return values](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#missing-return-values)                                                      | In scope |
| [Fee on transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)                                                                  | In scope |
| [Balance changes outside of transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) | In scope |
| [Upgradeability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#upgradable-tokens)                                                                 | In scope |
| [Flash minting](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#flash-mintable-tokens)                                                              | In scope |
| [Pausability](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#pausable-tokens)                                                                      | In scope |
| [Approval race protections](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#approval-race-protections)                                              | In scope |
| [Revert on approval to zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-approval-to-zero-address)                            | In scope |
| [Revert on zero value approvals](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-approvals)                                    | In scope |
| [Revert on zero value transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                    | In scope |
| [Revert on transfer to the zero address](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-transfer-to-the-zero-address)                    | In scope |
| [Revert on large approvals and/or transfers](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)                  | In scope |
| [Doesn't revert on failure](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#no-revert-on-failure)                                                   | In scope |
| [Multiple token addresses](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-zero-value-transfers)                                          | In scope |
| [Low decimals ( < 6)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#low-decimals)                                                                 | In scope |
| [High decimals ( > 18)](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#high-decimals)                                                              | In scope |
| [Blocklists](https://github.com/d-
  - docs/arweave.md: ## Cred

- cred (MERKLE) https://arweave.net/07UwhAbzabbVCONzOGFBI_RSGAR53VuIWg5QtLc8MPY
- address list https://arweave.net/iu9o8vHQmOyq0QzlY9nf4rHZqAOVCpQ6hJKcgm0PdYg
- merkle tree https://arweave.net/YasBn_PQuBwyNJ3LDdovhRJjYrtQZWl4S0MylkJkRF4

- cred (SIGNATURE) https://arweave.net/05h3kHrNG8iNcVcRPnQb6hdmdkjQ--NnmcteMirQQXg
- verifier list https://arweave.net/es6AuKe9D6etVyGccjyVqMWYf8SDN_hd2lS1BX48mVw
- whitelist https://arweave.net/ZTAqLQi4FJwohj17nzyIsAGZg_Cxjmp6CyQ7xY6aWzA

# Artwork

- art (BASIC) https://arweave.net/VTqPWOvHuWqGE1QJkWu03tMXE-a-c86551hYmGOGwlc
- art (ADVANCED) https://arweave.net/ySmBFIiD7EzlqPnLvGXASSIGIdv3rSMVKFTUhIH0ScA

  - docs/dev.md: ### Build

```sh
$ bun install
```

Build the contracts:

```sh
$ forge build
```

### Clean

Delete the build artifacts and cache directories:

```sh
$ forge clean
```

### Compile

Compile the contracts:

```sh
$ forge build
```

### Coverage

Get a test coverage report:

```sh
$ forge coverage --report summary --ir-minimum
```

### Deploy

forge script script/Deploy.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url cyber_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 111557560

forge script script/DeployBase.s.sol:Deploy --rpc-url optimism_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployWoCred.s.sol:Deploy --rpc-url arbitrum_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url sepolia --broadcast --verify --legacy --ffi

forge script script/DeployBase.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base_sepolia --broadcast --verify --legacy --ffi

forge script script/DeploySender.s.sol:Deploy --rpc-url optimism --broadcast --verify --legacy --ffi

forge script script/DeployDistributor.s.sol:Deploy --rpc-url base --broadcast --verify --legacy --ffi

forge script script/Deploy.s.sol:Deploy --rpc-url bera_testnet --broadcast

forge script script/DeployWoCred.s.sol:Deploy --rpc-url bera_testnet --broadcast --verify --verifier blockscout
--verifier-url https://api.socialscan.io/cyber-testnet/v1/explorer/command_api/contract --chain-id 80084

forge script script/DeployWoCred.s.sol:Deploy --rpc-url zora_sepolia --broadcast --verify --verifier blockscout
--verifier-url https://testnet.explorer.zora.energy/api\? --chain-id 999999999

forge script script/Deploy.s.sol:Deploy --broadcast --rpc-url bera_testnet --verifier-url
'https://api.routescan.io/v2/network/testnet/evm/80084/etherscan' --etherscan-api-key "verifyContract"

### Format

Format the contracts:

```sh
$ forge fmt
```

### Gas Usage

Get a gas report:

```sh
$ forge test --gas-report
```

### Lint

Lint the contracts:

```sh
$ bun run lint
```

### Test

Run the tests:

```sh
$ forge test
```

Generate test coverage and output result to the terminal:

```sh
$ bun run test:coverage
```

Generate test coverage with lcov report (you'll have to open the `./coverage/index.html` file in your browser, to do so
simply copy paste the path):

```sh
$ bun run test:coverage:report
```

## License

This project is licensed under MIT.

##

```
cloc ./src --by-file
      24 text files.
      24 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 2.00  T=0.05 s (527.7
  - docs/overview.md: # Phi Protocol Documentation

## Overview

Phi Protocol is a protocol for issuing and managing credentials on-chain and issuing NFTs linked to those creds. Cred
creators define creds by setting conditions, and users can obtain NFTs by meeting those conditions. Also, we are also
developing mint dapps based on this protocol layer.

## Architecture

Phi Protocol consists of the following main contracts:

1. **Cred**: Manages credential data.
2. **PhiFactory**: Manages the creation of NFTs.
3. **PhiNFT1155**: Manages NFTs representing credentials.
4. **PhiRewards**: Manages the distribution of rewards.
5. **BondingCurve**: Manages the bonding curve for credentials.
6. **CuratorRewardsDistributor**: Manages the distribution of curator rewards.
7. **ContributeRewards**: Manages additional rewards for credentials. (not audit scope)

![Architecture Diagram](./ArchitectureDiagram.png)

## Credential Creation

To create a credential, follow these steps:

1. Call the `createCred` function of the Cred contract, specifying the credential URL, verification type, bonding curve
   address, etc.
2. Credential data is stored in the Cred contract, and a new credential ID is issued.

### signature creation flow ![Sequence Diagram](./CreateCredSequence.png)

## NFT Creation and Claiming

To create NFTs linked to credentials, follow these steps:

1. Call the `createArt` function of the PhiFactory contract, passing the signed data and creation settings.
2. The PhiFactory contract deploys a new PhiNFT1155 contract or uses an existing contract to create NFTs.

Users can call the `merkleClaim` or `signatureClaim` function of the PhiFactory contract to claim NFTs if they meet the
conditions. 3. Each PhiNFT1155 contracts also have `merkleClaim` and `signatureClaim`. You can check this method in
Claimable.sol

## Additional Rewards

Using the ContributeRewards contract, additional rewards can be set for credentials.

1. Call the `setRewardInfo` function, specifying the cred ID, reward information (claim deadline, Merkle root, reward
   tokens, etc.).
2. Users can call the `claimReward` function, providing the Merkle proof to claim rewards.

## shareing (Curating) and Curator Rewards

Users can send shares to credentials by calling the `buyShareCred` function of the Cred contract. shareing requires ETH
calculated by the bonding curve. To cancel a share, use the `sellShareCred` function.

[Price Curve](https://docs.google.com/spreadsheets/d/18wHi9Mqo9YU8EUMQuUvuC75Dav6NSY5LOw-iDlkrZEA/edit?gid=859106557#gid=859106557)

Curators can call the `distribute` function of the CuratorRewardsDistributor contract to receive rewards based on the
amount of shares they hold.

## Reward Distribution

The PhiRewards contract manages the distribution of rewards to artists, referrers, and verifiers. The reward amounts are
defined in the contract's storage variables and can be updated by the owner.

## Upgradeability

The Cred, PhiFactory, and PhiNFT1155 contracts use the UUPS upgradeability pa
  - docs/users.md: ## Phi Protocol has 5 key types of users:

- Credential Creator
- Curator
- Verifier
- Artist
- Minter/Collector

---

- Credential Creator Credential Creators can suggest/create an Onchain credential by indexing blockchain data.

- Curator Curators show support for specific credentials by buying or selling Shares. Purchasing Shares helps the
  protocol understand which credentials are in higher demand. This is defined by the bonding curve for each Credential
  along with how early the Curator bought their share.

  Curators also earn a portion of mint fees for the credentials

- Verifier Verifier's help create the logical criteria to verify that the Minter is eligible to claim a credential by
  querying the user's onchain data. Verifier's achieve this by creating the backend validation logic and hosting this
  for Phi Protocol.

  Verifier's also earn a portion of mint fees for the credential they help verify.

- Artist Artists help create credential content which can be minted by Minters who want to collect the credentials.
  Multiple artists and artworks can be created for an onchain credential, which allows various styles of art to be
  collected. Artist's also earn a portion of mint fees for the credential they help verify.

- Collector Collectors focus on meeting eligibility requirements to collect Credentials. Collectors mint Credential
  NFT's and pay a small fee in the process.

  - Cred.sol (NatSpec): /// @title Cred
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
  - Cred.sol (NatSpec): /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
  - Cred.sol (NatSpec): /// @notice Pauses the contract.
  - Cred.sol (NatSpec): /// @notice Unpauses the contract.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
  - Cred.sol (NatSpec): /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
  - Cred.sol (NatSpec): /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
  - Cred.sol (NatSpec): /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Creates a new cred.
  - Cred.sol (NatSpec): /// @notice Updates the URL of a cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the price of a cred for a given amount.
    /// @param credId_ The ID of the cred.
    /// @param amount_ The amount to get the price for.
    /// @return The price of the cred for the given amount.
  - Cred.sol (NatSpec): /// @notice Gets the total buy price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total buy price for the batch.
  - Cred.sol (NatSpec): /// @notice Gets the total sell price for a batch of creds and amounts.
    /// @param credIds_ The IDs of the creds.
    /// @param amounts_ The amounts corresponding to each cred.
    /// @return The total sell price for the batch.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if a cred exists.
    /// @param credId_ The ID of the cred to check.
    /// @return Whether the cred exists.
  - Cred.sol (NatSpec): /// @notice Gets the information of a cred.
    /// @param credId_ The ID of the cred.
    /// @return The cred information.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Checks if an address has th cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return Whether the address has the cred.
  - Cred.sol (NatSpec): /// @notice Gets the number of share an address has for a cred.
    /// @param credId_ The ID of the cred.
    /// @param curator_ The address to check.
    /// @return The number of shares the address has for the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses that have the cred.
  - Cred.sol (NatSpec): /// @notice Gets the addresses and their share amounts.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their share amounts of the cred.
  - Cred.sol (NatSpec): /// @notice Gets the cred IDs and amounts for creds where the given address has a position
    /// @param  curator_ The address to check.
    /// @return credIds The IDs of the creds where the address has a position.
    /// @return amounts The corresponding amounts for each cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @notice Gets the root of a cred's Merkle tree.
    /// @param credId_ The ID of the cred.
    /// @return The root of the cred's Merkle tree.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to create a new cred.
    /// @param credURL_ The URL of the cred data.
    /// @param credType_ The type of the cred.
    /// @param verificationType_ The verification type of the cred.
    /// @param bondingCurve_ The address of the CuratePrice contract for the cred.
    /// @return The ID of the newly created cred.
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
    /// @dev Internal function to handle trade logic
    /// @param credId_ The ID of the cred
    /// @param amount_ The amount to buy or se;;
    /// @param isBuy True if buy, false if sell
    /// @param curator_ The address performing the action
    /// @param priceLimit The maximum price for the trade or minimum price for sell
  - Cred.sol (NatSpec): /// @dev Updates the balance for a user
    /// @param credId_ The ID of the cred
    /// @param sender_ The address of the user
    /// @param amount_ The amount to update
    /// @param isBuy True if Buy, false if Sell
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): //////////////////////////////////////////////////////////////*/
  - Cred.sol (NatSpec): /// @notice Helper function to get the addresses and their share amounts that have a cred.
    /// @param credId_ The ID of the cred.
    /// @param start_ The starting index for pagination.
    /// @param stop_ The stopping index for pagination.
    /// @return The addresses and their amounts of the cred
  - Cred.sol: // SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { EnumerableMap } from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import { UUPSUpgradeable } from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import { ECDSA } from "solady/utils/ECDSA.sol";

import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
import { LibString } from "solady/utils/LibString.sol";

import { ICred } from "./interfaces/ICred.sol";
import { IBondingCurve } from "./interfaces/IBondingCurve.sol";
import { IPhiRewards } from "./interfaces/IPhiRewards.sol";

/// @title Cred
contract Cred is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, PausableUpgradeable, ICred {
    /*//////////////////////////////////////////////////////////////
                                 USING
    //////////////////////////////////////////////////////////////*/
    using SafeTransferLib for address;
    using LibString for string;
    using LibString for uint256;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    /*//////////////////////////////////////////////////////////////
                                STORAGE
    //////////////////////////////////////////////////////////////*/
    uint16 private constant MAX_SUPPLY = 999;

    uint256 public constant SHARE_LOCK_PERIOD = 10 minutes;
    uint256 private immutable RATIO_BASE = 10_000;
    uint256 private immutable MAX_ROYALTY_RANGE = 5000;
    uint256 public credIdCounter;
    uint256 public protocolFeePercent;
    uint256 private locked;

    address public phiSignerAddress;
    address public protocolFeeDestination;
    address public phiRewardsAddress;

    mapping(uint256 credId => PhiCred creds) private creds;
    mapping(uint256 credId => bytes32 rood) public credsMerkeRoot;
    mapping(uint256 credId => EnumerableMap.AddressToUintMap balance) private shareBalance;
    mapping(uint256 credId => mapping(address curator => uint256 timestamp)) public lastTradeTimestamp;

    mapping(address priceCurve => bool enable) public curatePriceWhitelist;
    mapping(address curator => uint256[] credIds) private _credIdsPerAddress;
    mapping(address curator => mapping(uint256 credId => bool exist)) private _credIdExistsPerAddress;
    mapping(address curator => uint256 arrayLength) private _credIdsPerAddressArrLength;
    mapping(address curator => mapping(uint256 credId => uint256 index)) private _credIdsPerAddressCredIdIndex;

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    /// @custom:oz-upgrades-unsafe-allow constructor
    // solhint-disable-next-line func-visibility
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract.
    /// @param ownerAddress_ The address of the contract owner.
    /// @param protocolFeeDestination_ The address to receive protocol fees.
    /// @param protocolFeePercent_ The percentage of protocol fees. (100 = 1%)
    /// @param bondingCurveAddress_ The address of the CuratePrice contract.
    function initialize(
        address phiSignerAddress_,
        address ownerAddress_,
        address protocolFeeDestination_,
        uint256 protocolFeePercent_,
        address bondingCurveAddress_,
        address phiRewardsAddress_
    )
        external
        initializer
    {
        __Ownable_init(ownerAddress_);
        __Pausable_init();
        __UUPSUpgradeable_init();
        if (protocolFeeDestination_ == address(0)) {
            revert InvalidAddressZero();
        }
        locked = 1;
        credIdCounter = 1;
        phiSignerAddress = phiSignerAddress_;
        protocolFeeDestination = protocolFeeDestination_;
        phiRewardsAddress = phiRewardsAddress_;
        protocolFeePercent = protocolFeePercent_;
        curatePriceWhitelist[bondingCurveAddress_] = true;
    }

    function version() public pure returns (uint256) {
        return 1;
    }

    /// @notice Pauses the contract.
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract.
    function unPause() external onlyOwner {
        _unpause();
    }

    /*//////////////////////////////////////////////////////////////
                               MODIFIERS
    //////////////////////////////////////////////////////////////*/
    modifier nonReentrant() virtual {
        if (locked != 1) revert Reentrancy();
        locked = 2;
        _;
        locked = 1;
    }

    modifier nonZeroAddress(address address_) {
        if (address_ == address(0)) revert InvalidAddressZero();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                                  SET
    //////////////////////////////////////////////////////////////*/
    /// @notice Sets the claim signer address.
    /// @param phiSignerAddress_ The new claim signer address.
    function setPhiSignerAddress(address phiSignerAddress_) external nonZeroAddress(phiSignerAddress_) onlyOwner {
        phiSignerAddress = phiSignerAddress_;
        emit PhiSignerAddressSet(phiSignerAddress_);
    }

    /// @notice Sets the protocol fee destination.
    /// @param protocolFeeDestination_ The new protocol fee destination.
    function setProtocolFeeDestination(address protocolFeeDestination_)
        external
        nonZeroAddress(protocolFeeDestination_)
        onlyOwner
    {
        protocolFeeDestination = protocolFeeDestination_;
        emit ProtocolFeeDestinationChanged(_msgSender(), protocolFeeDestination_);
    }

    /// @notice Sets the protocol fee percentage.
    /// @param protocolFeePercent_ The new protocol fee percentage.
    function setProtocolFeePercent(uint256 protocolFeePercent_) external onlyOwner {
        protocolFeePercent = protocolFeePercent_;
        emit ProtocolFeePercentChanged(_msgSender(), protocolFeePercent_);
    }

    /// @notice Sets the PhiRewards contract address.
    /// @param phiRewardsAddress_ The new PhiRewards contract address.
    function setPhiRewardsAddress(address phiRewardsAddress_) external nonZeroAddress(phiRewardsAddress_) onlyOwner {
        phiRewardsAddress = phiRewardsAddress_;
        emit PhiRewardsAddressSet(phiRewardsAddress_);
    }

    /*//////////////////////////////////////////////////////////////
                             Whitelist
    //////////////////////////////////////////////////////////////*/
    /// @notice Adds an address to the whitelist.
    function addToWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = true;
        emit AddedToWhitelist(_msgSender(), address_);
    }

    /// @notice Removes an address from the whitelist.
    /// @param address_ The address to remove from the whitelist.
    function removeFromWhitelist(address address_) external onlyOwner {
        curatePriceWhitelist[address_] = false;
        emit RemovedFromWhitelist(_msgSender(), address_);
    }

    /*//////////////////////////////////////////////////////////////
                           Buy and Sell
    //////////////////////////////////////////////////////////////*/
    function buyShareCred(uint256 credId_, uint256 amount_, uint256 maxPrice_) public payable {
        _handleTrade(credId_, amount_, true, _msgSender(), maxPrice_);
    }

    function sellShareCred(uint256 credId_, uint256 amount_, uint256 minPrice_) public {
        _handleTrade(credId_, amount_, false, _msgSender(), minPrice_);
    }

    function buyShareCredFor(uint256 credId_, uint256 amount_, address curator_, uint256 maxPrice_) public payable {
        if (curato

_Determined via graph-gated Codex investigation (1 graph queries, 209s)._
