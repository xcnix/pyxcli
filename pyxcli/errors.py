##############################################################################
# Copyright 2016 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

from pyxcli.response import XCLIResponse
from pyxcli.helpers.xml_util import ElementNotFoundException
from pyxcli.helpers import xml_util as etree


class XCLIError(Exception):
    """Base class of all XCLI-related errors"""
    pass


class BaseScsiException(Exception):
    pass


class CommandExecutionError(XCLIError):
    """
    Base class of all XCLI command execution errors: invalid command,
    parameters, operation failed, etc. This is the "stable API" for
    catching XCLI exceptions - there are subclasses for specific errors,
    but these should be considered unstable and may change over time
    """
    KNOWN_CODES = {}
    KNOWN_LEVELS = {}

    def __init__(self, code, status, xml, return_value=None):
        XCLIError.__init__(self, code, status, xml)
        self.code = code
        self.status = status
        self.xml = xml
        if return_value is not None:
            self.return_value = return_value
        else:
            self.return_value = XCLIResponse(xml)

    def __str__(self):
        return self.status

    @classmethod
    def instantiate(cls, rootelem, cmdroot, encoding):
        try:
            # "code/@value"
            code = etree.xml_find(cmdroot, "code", "value")
            # "status/@value"
            level = etree.xml_find(cmdroot, "status", "value")
            # "status_str/@value"
            status = etree.xml_find(cmdroot, "status_str", "value")
        except ElementNotFoundException:
            code = None
            level = None
            status = "Unknown reason"

        xcli_response = XCLIResponse.instantiate(cmdroot, encoding)

        if code in cls.KNOWN_CODES:
            concrete = cls.KNOWN_CODES[code]
        elif level in cls.KNOWN_LEVELS:
            concrete = cls.KNOWN_LEVELS[level]
        else:
            concrete = CommandFailedUnknownReason
        return concrete(code, status, cmdroot, xcli_response)

    @classmethod
    def register(cls, *codes):
        def deco(concrete):
            for code in codes:
                cls.KNOWN_CODES[code] = concrete
            return concrete
        return deco

    @classmethod
    def register_level(cls, *codes):
        def deco(concrete):
            for code in codes:
                cls.KNOWN_LEVELS[code] = concrete
            return concrete
        return deco


class CommandFailedUnknownReason(CommandExecutionError):
    pass


##############################################################################
# Concrete Error Levels
##############################################################################
@CommandExecutionError.register_level("1")
class CommandFailedConnectionError(CommandExecutionError):
    pass


@CommandExecutionError.register_level("2")
class CommandFailedSyntaxError(CommandExecutionError):
    pass


@CommandExecutionError.register_level("3")
class CommandFailedRuntimeError(CommandExecutionError):
    pass


@CommandExecutionError.register_level("4")
class CommandFailedPassiveManager(CommandExecutionError):
    pass


@CommandExecutionError.register_level("5")
class CommandFailedInternalError(CommandExecutionError):
    pass


##############################################################################
# Concrete Error Codes
##############################################################################
@CommandExecutionError.register("MCL_TIMEOUT")
class MCLTimeoutError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_MASTER")
class VolumeMasterError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("PARTIAL_SUCCESS")
class PartialSuccessError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TRNS_ERROR_WITH_EXTENDED_INFO")
class OperationFailedWithExtendedInfoError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_BAD_NAME")
class VolumeBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SOURCE_VOLUME_BAD_NAME")
class SourceVolumeBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_VOLUME_BAD_NAME")
class TargetVolumeBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("BASE_VOLUME_BAD_NAME")
class BaseVolumeBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("BASE_VOLUME_INVALID")
class BaseVolumeInvalidError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_EXISTS")
class VolumeExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_MAPPED")
class VolumeIsMappedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_SIZE_ABOVE_LIMIT")
class VolumeSizeAboveLimitError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_NO_MIRROR")
class VolumeHasNoMirrorError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_DATA_MIGRATION")
class VolumeHasDataMigrationError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_BELONGS_TO_MIRRORED_CONS_GROUP")
class VolumeIsPartOfMirroredCgError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("ALU_BAD_NAME")
class ALUBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_BAD_NAME")
class CgBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_NO_MIRROR")
class CgHasNoMirrorError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_NOT_SYNCHRONIZED")
class MirrorNotSynchronizedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_ASYNC")
class MirrorIsAsyncError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_INITIAL")
class MirrorInitializingError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_ACTIVE")
class MirrorActiveError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SYNC_ALREADY_INACTIVE")
class SyncAlreadyInactiveError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SYNC_ALREADY_ACTIVE")
class SyncAlreadyActiveError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_NON_OPERATIONAL")
class MirrorNonOperationalError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_TARGET_NOT_CONNECTED")
class RemoteTargetNotConnectedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LOCAL_PEER_IS_NOT_MASTER")
class LocalIsNotMasterError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("NOT_ENOUGH_SPACE")
class PoolOutOfSpaceError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("NOT_ENOUGH_HARD_SPACE")
class PoolOutOfHardSpaceError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("NOT_ENOUGH_SNAPSHOT_SPACE")
class PoolOutOfSnapshotSpaceError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("NO_SPACE")
class SystemOutOfSpaceError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("NOT_ENOUGH_SPACE_ON_REMOTE_MACHINE")
class RemotePoolOutOfSpaceError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_SNAPSHOT")
class OperationNotPermittedOnSnapshotError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("BAD_PARAMS")
class BadParameterError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HOST_NAME_EXISTS")
class HostNameAlreadyExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HOST_PORT_EXISTS")
class HostWithPortIdAlreadyDefined(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("POOL_DOES_NOT_EXIST")
class PoolDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("POOL_SNAPSHOT_LIMIT_REACHED")
class PoolSnapshotLimitReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_VOLUME_IS_MASTER")
class RemoteVolumeIsMasterError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONF_PATH_DOES_NOT_EXIST")
class PathDoesNotExistInConfigurationError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("ILLEGAL_VALUE")
class IllegalValueForArgumentError(CommandFailedSyntaxError):
    pass


@CommandExecutionError.register("ILLEGAL_NAME")
class IllegalNameForObjectError(CommandFailedSyntaxError):
    pass


@CommandExecutionError.register("COMPONENT_TYPE_MUST_HAVE_COMPONENT_ID")
class ComponentTypeMustHaveComponentIDError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HOST_PROFILE_UPDATE_TOO_FREQUENT")
class HostProfileUpdateTooFrequentError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HOST_BAD_NAME")
class HostBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CLUSTER_BAD_NAME")
class ClusterBadNameError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_HOST_PROFILES_REACHED")
class MaxHostProfilesReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SSD_CACHING_NOT_ENABLED")
class SSDCachingNotEnabledError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("UNRECOGNIZED_EVENT_CODE")
class UnrecognizedEventCodeError(CommandFailedSyntaxError):
    pass


@CommandExecutionError.register("UNRECOGNIZED_COMMAND")
class UnrecognizedCommandError(CommandFailedSyntaxError):
    pass


@CommandExecutionError.register("CAN_NOT_SHRINK_VOLUME")
class VolumeSizeCannotBeDecreased(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("OBJECT_BAD_NAME")
class ReferencedObjectDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("OPERATION_FORBIDDEN_FOR_USER_CATEGORY")
class OperationForbiddenForUserCategoryError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("ACCESS_DENIED")
class AccessDeniedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMMAND_NOT_SUPPORTED_FOR_OLVM_VOLUMES")
class CommandNotSupportedForOLVMVolumes(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_LOCKED")
class VolumeLocked(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_OLVM")
class VolumeHasOlvm(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_MIRROR")
class VolumeHasMirrorError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_BELONGS_TO_CG")
class VolumeBelongsToCGError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_MAX_DB_REACHED")
class MetadataServiceMaxDBReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_DB_DOES_NOT_EXIST")
class MetadataServiceDBDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_DB_ALREADY_EXISTS")
class MetadataServiceDBAlreadyExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_KEY_DOES_NOT_EXIST")
class MetadataServiceKeyDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("KEY_DOES_NOT_EXIST")
class KeyDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_KEY_ALREADY_EXISTS")
class MetadataServiceKeyAlreadyExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("KEY_EXISTS")
class KeyExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_MAX_ENTRIES_REACHED")
class MetadataServiceMaxEntriesReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("STATUS_METADATA_SERVICE_INVALID_TOKEN")
class MetadataServiceInvalidTokenError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LDAP_AUTHENTICATION_IS_NOT_ACTIVE")
class LDAPAuthenticationIsNotActive(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LDAP_IS_NOT_FULLY_CONFIGURED")
class LDAPIsNotFullyConfigured(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_INCOMPATIBLE_SIZE")
class VolumeIncompatibleSizeError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSION_DISABLED")
class CompressionDisabledError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSION_REQUIRES_THIN_PROVISIONED_POOL")
class CompressionRequiresThinPoolError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSED_VOLUMES_LIMIT_REACHED")
class CompressedVolumesLimitReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSED_CAPACITY_LIMIT_REACHED")
class CompressedCapacityLimitReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSED_VOLUME_TOO_BIG")
class CompressedVolumeTooBigError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSED_VOLUME_TOO_SMALL")
class CompressedVolumeTooSmallError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SOURCE_VOLUME_COMPRESSED_TARGET_UNCOMPRESSED")
class SourceVolumeCompressedTargetUncompressedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SOURCE_VOLUME_UNCOMPRESSED_TARGET_COMPRESSED")
class SourceVolumeUncompressedTargetCompressedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CANNOT_SHRINK_COMPRESSED_VOLUME")
class CannotShrinkCompressedVolumeError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_TRANSFORM")
class VolumeHasTransformError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_COMPRESSED")
class VolumeIsCompressedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("COMPRESSED_VOLUME_IS_MAPPED")
class CompressedVolumeIsMappedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CAN_NOT_MAP_SLAVE_COMPRESSED_VOLUME")
class CannotMapSlaveError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_NAME_EXISTS")
class CgNameExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_DOES_NOT_EXIST")
class CgDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_CONS_GROUPS_REACHED")
class CgLimitReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_HAS_MIRROR")
class CgHasMirrorError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_NOT_EMPTY")
class CgNotEmptyError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_EMPTY")
class CgEmptyError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MISMATCH")
class CgMismatchError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MIRROR_PARAMS_MISMATCH")
class CgMirrorParamsMismatchError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MIRRORING_NOT_SUPPORTED_IN_TARGET")
class CgMirroringNotSupportedOnTargetError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_GROUP_BAD_NAME")
class SnapshotGroupDoesNotExistError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_IS_MAPPED")
class SnapshotIsMappedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_HAS_ACTIVE_SYNC_JOB")
class SnapshotIsSynchronisingError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_VOLUMES_REACHED")
class MaxVolumesReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("DOMAIN_MAX_VOLUMES_REACHED")
class DomainMaxVolumesReachedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_GROUP_BAD_PREFIX")
class SnapshotGroupIsReservedError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_GROUP_NAME_EXISTS")
class SnapshotGroupAlreadyExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register(
    "OVERWRITE_SNAPSHOT_GROUP_DOES_NOT_BELONG_TO_GIVEN_GROUP")
class SnapshotGroupMismatchError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_NOT_CONNECTED_TO_ANY_PERF_CLASS")
class VolumeNotConnectedToPerfClassError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("PERF_CLASS_BAD_NAME")
class PerfClassNotExistsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_ALREADY_IN_PERF_CLASS")
class VolumeAlreadyInPerfClassError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("PERF_CLASS_ASSOCIATED_WITH_HOSTS")
class PerfClassAssociatedWithHostError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("PERF_CLASS_ASSOCIATED_WITH_POOLS_OR_DOMAINS")
class PerfClassAssociatedWithPoolsOrDomainsError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("PERF_CLASS_ASSOCIATED_WITH_VOLUMES")
class PerfClassAssociatedWithVolumesError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_IS_SLAVE")
class ConsGroupIsSlave(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_VOLUMES_IN_CONS_GROUP_REACHED")
class MaxVolumesInConsGroupReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_VOLUMES_IN_REMOTE_CONS_GROUP_REACHED")
class MaxVolumesInRemoteConsGroupReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_VOLUME_BAD_POOL")
class RemoteVolumeBadPool(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_VOLUME_BELONGS_TO_CONS_GROUP")
class RemoteVolumeBelongsToConsGroup(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_BAD_POOL")
class VolumeBadPool(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_NOT_IN_CONS_GROUP")
class VolumeNotInConsGroup(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_VOLUMES_REACHED")
class RemoteMaxVolumesReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_VOLUME_EXISTS")
class RemoteVolumeExists(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_SLAVE")
class VolumeIsSlave(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_STANDBY_RELATION_ALREADY_DEFINED")
class StandbyAlreadyDefined(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register(
    "TRNS_MGMT_STATUS_OBJECTS_IN_DIFFERENT_DOMAINS")
class StorageObjectIsNotInDomain(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_BAD_TARGET")
class ConsGroupBadTarget(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_HA_ACTIVATION_MISMATCH")
class ConsGroupHaActivationMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_HA_ROLE_MISMATCH")
class ConsGroupHaRoleMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_HA_TARGET_MISMATCH")
class ConsGroupHaTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_IS_NOT_HA")
class ConsGroupIsNotHa(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_IS_NOT_MULTISITE")
class ConsGroupIsNotMultisite(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MEMBER_VOL_IS_MISSING_A_RELATION")
class ConsGroupMemberVolIsMissingARelation(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MIRROR_OR_HA_TYPE_MISMATCH")
class ConsGroupMirrorOrHaTypeMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MIRROR_ROLE_MISMATCH")
class ConsGroupMirrorRoleMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_MIRROR_SCHEDULE_MISMATCH")
class ConsGroupMirrorScheduleMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("CONS_GROUP_RELATION_PART_OF_MULTISITE_MISMATCH")
class ConsGroupRelationPartOfMultisiteMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("DATA_REDUCTION_TIER_IS_OFFLINE")
class DataReductionTierIsOffline(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_ASSOCIATED_WITH_MULTISITE")
class HaAssociatedWithMultisite(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_BAD_ID")
class HaBadId(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_CONFIGURATION_ERROR")
class HaConfigurationError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_CONNECTIVITY_NOT_SUFFICIENT")
class HaConnectivityNotSufficient(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_HAS_SYNC_JOB")
class HaHasSyncJob(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_HIGH_AVAILABILITY_DISABLED_IN_VOL")
class HaHighAvailabilityDisabledInVol(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_HIGH_AVAILABILITY_ENABLED_IN_VOL")
class HaHighAvailabilityEnabledInVol(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_INCOMPATIBLE_TARGET_VERSION")
class HaIncompatibleTargetVersion(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_IS_ACTIVE")
class HaIsActive(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_IS_INITIAL")
class HaIsInitial(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_IS_NON_OPERATIONAL")
class HaIsNonOperational(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_IS_NOT_OPERATIONAL")
class HaIsNotOperational(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_IS_NOT_SYNCHRONIZED")
class HaIsNotSynchronized(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_LAST_SYNC_TIMES_DIFFER")
class HaLastSyncTimesDiffer(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_PART_OF_MULTISITE")
class HaPartOfMultisite(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HA_RETRY_OPERATION")
class HaRetryOperation(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HOST_TYPE_IS_NOT_CONFIGURED")
class HostTypeIsNotConfigured(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HYPERSWAP_EXISTS_ON_TARGET")
class HyperswapExistsOnTarget(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("HYPERSWAP_EXISTS_ON_VOLUME")
class HyperswapExistsOnVolume(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LOCAL_AND_REMOTE_VOLUME_NAMES_ARE_DIFFERENT")
class LocalAndRemoteVolumeNamesAreDifferent(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LOCAL_MAX_HA_REACHED")
class LocalMaxHaReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("LOCAL_PEER_HAS_NO_QUORUM_CONNECTIVITY")
class LocalPeerHasNoQuorumConnectivity(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MASTER_CANNOT_BE_DEMOTED")
class MasterCannotBeDemoted(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_NUM_OF_PROXY_VOLUME_REACHED")
class MaxNumOfProxyVolumeReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAX_SNAPSHOTS_PER_VOLUME_REACHED")
class MaxSnapshotsPerVolumeReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_CAN_NOT_BE_ACTIVATED")
class MirrorCanNotBeActivated(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_CONFIGURATION_ERROR")
class MirrorConfigurationError(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_EXISTS_ON_TARGET")
class MirrorExistsOnTarget(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_HAS_NO_SYNCHED_SNAPSHOT")
class MirrorHasNoSynchedSnapshot(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_IS_STANDBY")
class MirrorIsStandby(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_OF_SAME_TYPE_EXISTS_ON_VOLUME")
class MirrorOfSameTypeExistsOnVolume(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_PART_OF_MULTISITE")
class MirrorPartOfMultisite(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_RETRY_OPERATION")
class MirrorRetryOperation(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_SIZE_MISMATCH")
class MirrorSizeMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_TYPE_IS_NOT_SYNC")
class MirrorTypeIsNotSync(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_ALREADY_DEFINED")
class MultisiteAlreadyDefined(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_ASYNC_MIRROR_IS_ACTIVE")
class MultisiteAsyncMirrorIsActive(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_ASYNC_MIRROR_IS_NOT_CONNECTED")
class MultisiteAsyncMirrorIsNotConnected(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_MASTER_SMASTER_CLOCK_SKEW_TOO_BIG")
class MultisiteMasterSmasterClockSkewTooBig(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_NOT_OPERATIONAL")
class MultisiteNotOperational(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SLAVE_MASTER_RELATION_IS_MISSING")
class MultisiteSlaveMasterRelationIsMissing(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SLAVE_MASTER_TARGET_MISMATCH")
class MultisiteSlaveMasterTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SLAVE_SMASTER_TARGET_MISMATCH")
class MultisiteSlaveSmasterTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SLAVE_TARGET_NOT_CONNECTED")
class MultisiteSlaveTargetNotConnected(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_HAS_NO_SYNCHED_SNAPSHOT")
class MultisiteSmasterHasNoSynchedSnapshot(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_INVALID_CONFIGURATION")
class MultisiteSmasterInvalidConfiguration(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_INVALID_MIRROR_STATE")
class MultisiteSmasterInvalidMirrorState(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_INVALID_RELATION_STATE")
class MultisiteSmasterInvalidRelationState(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_MASTER_RELATION_IS_MISSING")
class MultisiteSmasterMasterRelationIsMissing(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_MASTER_TARGET_MISMATCH")
class MultisiteSmasterMasterTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_SLAVE_TARGET_MISMATCH")
class MultisiteSmasterSlaveTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_SMASTER_TARGET_NOT_CONNECTED")
class MultisiteSmasterTargetNotConnected(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_STANDBY_MIRROR_ALREADY_DEFINED")
class MultisiteStandbyMirrorAlreadyDefined(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_STANDBY_MIRROR_IS_NOT_CONNECTED")
class MultisiteStandbyMirrorIsNotConnected(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_STANDBY_MIRROR_NOT_REGISTERED")
class MultisiteStandbyMirrorNotRegistered(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_TOO_MANY_ACTIVE_RELATIONS")
class MultisiteTooManyActiveRelations(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("OPERATION_NOT_ALLOWED_ON_LOOPBACK")
class OperationNotAllowedOnLoopback(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("OVERWRITE_SNAPSHOT_BAD_NAME")
class OverwriteSnapshotBadName(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("RELATION_RETRY_OPERATION")
class RelationRetryOperation(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_CONS_GROUP_BAD_NAME")
class RemoteConsGroupBadName(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_CONS_GROUP_EMPTY")
class RemoteConsGroupEmpty(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_CONS_GROUP_MISMATCH")
class RemoteConsGroupMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_CONS_GROUP_NOT_EMPTY")
class RemoteConsGroupNotEmpty(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_DATA_REDUCTION_TIER_IS_OFFLINE")
class RemoteDataReductionTierIsOffline(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_DOMAIN_MAX_VOLUMES_REACHED")
class RemoteDomainMaxVolumesReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_HA_IS_NOT_ACTIVE")
class RemoteHaIsNotActive(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_HA_IS_STANDBY")
class RemoteHaIsStandby(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_HA_REACHED")
class RemoteMaxHaReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_METADATA_OBJECTS_REACHED")
class RemoteMaxMetadataObjectsReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_NUM_OF_PROXY_VOLUME_REACHED")
class RemoteMaxNumOfProxyVolumeReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_SNAPSHOTS_FOR_VOLUME_REACHED")
class RemoteMaxSnapshotsForVolumeReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAX_SNAPSHOTS_PER_VOLUME_REACHED")
class RemoteMaxSnapshotsPerVolumeReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MAY_NOT_HAVE_COMPLETED_THE_OPERATION")
class RemoteMayNotHaveCompletedTheOperation(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_MIRROR_IS_STANDBY")
class RemoteMirrorIsStandby(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_POOL_SNAPSHOT_LIMIT_REACHED")
class RemotePoolSnapshotLimitReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SNAPSHOT_BAD_PREFIX")
class RemoteSnapshotBadPrefix(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SNAPSHOT_GROUP_ILLEGAL_PRIORITY")
class RemoteSnapshotGroupIllegalPriority(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SNAPSHOT_GROUP_NAME_EXISTS")
class RemoteSnapshotGroupNameExists(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SNAPSHOT_ILLEGAL_PRIORITY")
class RemoteSnapshotIllegalPriority(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SNAPSHOT_NAME_EXISTS")
class RemoteSnapshotNameExists(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_SYSTEM_OUT_OF_PHYSICAL_SPACE")
class RemoteSystemOutOfPhysicalSpace(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_TARGET_HAS_NO_QUORUM_WITNESS")
class RemoteTargetHasNoQuorumWitness(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_VOLUME_IS_SNAPSHOT")
class RemoteVolumeIsSnapshot(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SLAVE_VOLUME_IS_MAPPED")
class SlaveVolumeIsMapped(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_GROUP_ILLEGAL_PRIORITY")
class SnapshotGroupIllegalPriority(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_GROUP_IS_INTERNAL")
class SnapshotGroupIsInternal(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_ILLEGAL_PRIORITY")
class SnapshotIllegalPriority(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_IS_INTERNAL")
class SnapshotIsInternal(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SNAPSHOT_IS_PART_OF_SNAPSHOT_GROUP")
class SnapshotIsPartOfSnapshotGroup(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("SYSTEM_OUT_OF_PHYSICAL_SPACE")
class SystemOutOfPhysicalSpace(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_BAD_NAME")
class TargetBadName(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_BAD_TYPE")
class TargetBadType(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_HAS_ENABLED_HA")
class TargetHasEnabledHa(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_PEER_NOT_HEALTHY")
class TargetPeerNotHealthy(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_VOLUME_HAS_OLVM")
class TargetVolumeHasOlvm(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_BAD_PREFIX")
class VolumeBadPrefix(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_HA")
class VolumeHasHa(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_MULTIPLE_MIRRORS")
class VolumeHasMultipleMirrors(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_HAS_STANDBY_SNAPSHOTS")
class VolumeHasStandbySnapshots(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_NOT_CONSISTENT_SLAVE")
class VolumeIsNotConsistentSlave(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_NOT_HA")
class VolumeIsNotHa(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_IS_NOT_MULTISITE")
class VolumeIsNotMultisite(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("VOLUME_TARGET_MISMATCH")
class VolumeTargetMismatch(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("TARGET_VOLUME_HAS_HA")
class TargetVolumeHasHa(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("REMOTE_ACTION_FAILED")
class RemoteActionFailed(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_DELETE_PARTIAL"
                                "_FAILURE_MANUAL_CLEANUP_REQUIRED")
class MultisitePartialDelete(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("RPC_READ_RESPONSE_FAILED")
class RpcReadResponseFailed(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("ERROR")
class GeneralError(CommandFailedRuntimeError):
    pass

@CommandExecutionError.register("MULTISITE_MASTER_INVALID_CONFIGURATION")
class MultisiteMasterInvalidConfiguration(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MAPPING_IS_NOT_DEFINED")
class MappingIsNotDefined(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MULTISITE_MAX_NUM_OF_MIRRORS_REACHED")
class MultisiteMaxNumOfMirrorsReached(CommandFailedRuntimeError):
    pass


@CommandExecutionError.register("MIRROR_ASSOCIATED_WITH_MULTISITE")
class MirrorAssociatedWithMultisite(CommandFailedRuntimeError):
    pass
##############################################################################
# CredentialsError
# we explicitly want to differentiate CredentialsError from
# CommandExecutionError, so although it is raised by _build_response,
# it derives from XCLIError directly
##############################################################################


@CommandExecutionError.register("LOGIN_FAILURE_USER_FAILED_TO_LOGIN",
                                "USER_NAME_DOES_NOT_EXIST",
                                "DEFAULT_USER_IS_NOT_DEFINED",
                                "INCORRECT_PASSWORD",
                                "USER_OR_PASSWORD_WRONG_OR_MISSING",
                                "LOGIN_FAILURE_USER_NOT_FOUND_IN_LDAP_SERVERS",
                                "LOGIN_FAILURE_USER_NOT_AUTHENTICATED_BY_ \
                                LDAP_SERVER")
class CredentialsError(XCLIError):
    """Raises when an XCLI command fails due to invalid credentials.
    Inherits directly from XCLIError, not CommandExecutionError,
    although it is raised during the execution of a command
    to explicitly differentiate the two
    """
    def __init__(self, code, status, xml, return_value=None):
        XCLIError.__init__(self, code, status, xml)
        self.code = code
        self.status = status
        self.xml = xml
        if return_value is not None:
            self.return_value = return_value
        else:
            self.return_value = XCLIResponse(xml)

    def __str__(self):
        ret_str = ""
        if isinstance(self.xml, str):
            ret_str = "%s\n\n%s" % (self.status, self.xml)
        else:
            ret_str = "%s\n\n%s" % (etree.tostring(self.xml))
        return ret_str


##############################################################################
# AServer ("delivery") errors
##############################################################################
class CommandFailedAServerError(CommandExecutionError):
    """AServer related errors"""

    REMOTE_TARGET_ERRORS = frozenset(["TARGET_IS_NOT_CONNECTED",
                                      "TARGET_DOES_NOT_EXIST",
                                      "SEND_TO_TARGET_FAILED",
                                      "GETTING_RESPONSE_FROM_TARGET_FAILED"])

    @classmethod
    def instantiate(cls, aserver, rootelem):
        if aserver in cls.REMOTE_TARGET_ERRORS:
            return CommandFailedRemoteTargetError(aserver, aserver, rootelem)
        else:
            return CommandFailedAServerError(aserver, aserver, rootelem)


class CommandFailedRemoteTargetError(CommandFailedAServerError):
    pass


##############################################################################
# Misc
##############################################################################
class UnsupportedNextraVersion(XCLIError):
    pass


class CorruptResponse(XCLIError):
    pass


##############################################################################
# Transport
##############################################################################
class TransportError(XCLIError):
    """Base class of all transport-related errors"""
    pass


class ConnectionError(TransportError):
    """Represents errors that occur during connection"""
    pass


class RanOutOfEndpointError(IOError, TransportError):
    pass
