from enum import IntEnum
from typing import Any, NamedTuple, Optional, Protocol, Union

from ..constants import (AccountFlags, AccountTxFlags, DerivationType, KeyInstanceFlag,
    MasterKeyFlags, NetworkServerFlag, NetworkServerType, PaymentFlag,
    PeerChannelAccessTokenFlag, PeerChannelMessageFlag, PushDataMatchFlag,
    PushDataHashRegistrationFlag, ScriptType,
    ServerPeerChannelFlag, TransactionOutputFlag, TxFlags, WalletEventFlag, WalletEventType)
from ..types import MasterKeyDataTypes


class AccountRow(NamedTuple):
    account_id: int
    default_masterkey_id: Optional[int]
    default_script_type: ScriptType
    account_name: str
    flags: AccountFlags
    indexer_server_id: Optional[int]
    peer_channel_server_id: Optional[int]


class AccountTransactionDescriptionRow(NamedTuple):
    account_id: int
    tx_hash: bytes
    description: Optional[str]


class AccountTransactionRow(NamedTuple):
    account_id: int
    tx_hash: bytes
    flags: AccountTxFlags
    description: Optional[str]
    date_created: int
    date_updated: int


class SpentOutputRow(NamedTuple):
    spent_tx_hash: bytes
    spent_txo_index: int
    spending_tx_hash: bytes
    spending_txi_index: int
    block_hash: Optional[bytes]
    flags: TxFlags


class HistoryListRow(NamedTuple):
    tx_hash: bytes
    tx_flags: TxFlags
    block_hash: Optional[bytes]
    block_height: int
    block_position: Optional[int]
    description: Optional[str]
    value_delta: int
    date_created: int


class InvoiceAccountRow(NamedTuple):
    invoice_id: int
    payment_uri: str
    description: Optional[str]
    flags: PaymentFlag
    value: int
    date_expires: Optional[int]
    date_created: int


class InvoiceRow(NamedTuple):
    invoice_id: int
    account_id: int
    tx_hash: Optional[bytes]
    payment_uri: str
    description: Optional[str]
    flags: PaymentFlag
    value: int
    invoice_data: bytes
    date_expires: Optional[int]
    date_created: int = -1


class KeyDataProtocol(Protocol):
    # Overlapping common output/spendable type field.
    @property
    def keyinstance_id(self) -> int:
        ...
    # Spendable type fields.
    @property
    def account_id(self) -> int:
        ...
    @property
    def masterkey_id(self) -> Optional[int]:
        ...
    @property
    def derivation_type(self) -> DerivationType:
        ...
    @property
    def derivation_data2(self) -> Optional[bytes]:
        ...


# @dataclasses.dataclass
class KeyData(NamedTuple):
    keyinstance_id: int                 # Overlapping common output/spendable type field.
    account_id: int                     # Spendable type field.
    masterkey_id: Optional[int]         # Spendable type field.
    derivation_type: DerivationType     # Spendable type field.
    derivation_data2: Optional[bytes]   # Spendable type field.


class KeyInstanceFlagRow(NamedTuple):
    keyinstance_id: int
    flags: KeyInstanceFlag


class KeyInstanceFlagChangeRow(NamedTuple):
    keyinstance_id: int
    flags_old: KeyInstanceFlag
    flags_new: KeyInstanceFlag=KeyInstanceFlag.NONE


class KeyInstanceRow(NamedTuple):
    keyinstance_id: int                 # Overlapping common output/spendable type field.
    account_id: int                     # Spendable type field.
    masterkey_id: Optional[int]         # Spendable type field.
    derivation_type: DerivationType     # Spendable type field.
    derivation_data: bytes
    derivation_data2: Optional[bytes]   # Spendable type field.
    flags: KeyInstanceFlag
    description: Optional[str]


class KeyInstanceScriptHashRow(NamedTuple):
    keyinstance_id: int
    script_type: ScriptType
    script_hash: bytes


class KeyListRow(NamedTuple):
    account_id: int
    keyinstance_id: int                 # Overlapping common output/spendable type field.
    masterkey_id: Optional[int]         # Spendable type field.
    derivation_type: DerivationType     # Spendable type field.
    derivation_data: bytes
    derivation_data2: Optional[bytes]   # Spendable type field.
    flags: KeyInstanceFlag
    description: Optional[str]
    date_updated: int
    txo_value: int
    txo_count: int


class MasterKeyRow(NamedTuple):
    masterkey_id: int
    parent_masterkey_id: Optional[int]
    derivation_type: DerivationType
    derivation_data: bytes
    flags: MasterKeyFlags


# WARNING The order of the fields in this data structure are implicitly linked to the query.
class NetworkServerRow(NamedTuple):
    # If this is `None` on an INSERT, SQLite will substitute it for a real primary key value.
    server_id: Optional[int]
    server_type: NetworkServerType
    url: str
    account_id: Optional[int]
    server_flags: NetworkServerFlag
    api_key_template: Optional[str]
    encrypted_api_key: Optional[str]
    # MAPI specific: used for JSONEnvelope serialised transaction fee quotes.
    mapi_fee_quote_json: Optional[str]
    # Indexer server specific: used for tip filter notifications.
    tip_filter_peer_channel_id: Optional[int]
    date_last_try: int
    date_last_good: int
    date_created: int
    date_updated: int


class PasswordUpdateResult(NamedTuple):
    password_token: str
    account_private_key_updates: dict[int, list[tuple[int, str]]]
    masterkey_updates: list[tuple[int, DerivationType, MasterKeyDataTypes]]


class PushDataRegistrationRow(NamedTuple):
    pushdata_flags: int
    date_created: int
    duration_seconds: int


class PaymentRequestReadRow(NamedTuple):
    paymentrequest_id: int
    keyinstance_id: int
    state: PaymentFlag
    requested_value: Optional[int]
    received_value: Optional[int]
    expiration: Optional[int]
    description: Optional[str]
    script_type: ScriptType
    pushdata_hash: bytes
    date_created: int = -1


class PaymentRequestRow(NamedTuple):
    paymentrequest_id: int
    keyinstance_id: int
    state: PaymentFlag
    requested_value: Optional[int]
    expiration: Optional[int]
    description: Optional[str]
    script_type: ScriptType
    pushdata_hash: bytes
    date_created: int = -1


class PaymentRequestUpdateRow(NamedTuple):
    state: PaymentFlag
    value: Optional[int]
    expiration: Optional[int]
    description: Optional[str]
    paymentrequest_id: int


SpendConflictType = tuple[bytes, int, bytes, int]


class TransactionDeltaSumRow(NamedTuple):
    account_id: int
    total: int
    match_count: int


class TransactionDescriptionResult(NamedTuple):
    tx_hash: bytes
    description: str


class TransactionExistsRow(NamedTuple):
    tx_hash: bytes
    flags: TxFlags
    account_id: Optional[int]


class TransactionInputAddRow(NamedTuple):
    tx_hash: bytes
    txi_index: int
    spent_tx_hash: bytes
    spent_txo_index: int
    sequence: int
    flags: int
    script_offset: int
    script_length: int
    date_created: int
    date_updated: int


class TransactionLinkState:
    # Parameters.
    rollback_on_spend_conflict: bool = False
    # Results.
    has_spend_conflicts: bool = False
    account_ids: Optional[set[int]] = None


class TransactionMetadata(NamedTuple):
    block_hash: Optional[bytes]
    block_position: Optional[int]
    fee_value: Optional[int]
    date_created: int


class TransactionOutputCommonProtocol(Protocol):
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    flags: TransactionOutputFlag
    script_type: ScriptType


class TransactionOutputAddRow(NamedTuple):
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    script_type: ScriptType
    flags: TransactionOutputFlag
    script_hash: bytes
    script_offset: int
    script_length: int
    date_created: int
    date_updated: int


class TransactionOutputShortRow(NamedTuple):
    # Standard transaction output fields.
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    flags: TransactionOutputFlag
    script_type: ScriptType
    # Extension fields for this type.
    script_hash: bytes


class TransactionOutputFullRow(NamedTuple):
    # Standard transaction output fields.
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    flags: TransactionOutputFlag
    script_type: ScriptType
    # Extension fields for this type.
    script_hash: bytes
    script_offset: int
    script_length: int
    spending_tx_hash: Optional[bytes]
    spending_txi_index: Optional[int]


class AccountTransactionOutputSpendableRow(NamedTuple):
    """
    Transaction output data with the additional key instance information required for spending it.
    """
    # Standard transaction output fields.
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    script_type: ScriptType
    flags: TransactionOutputFlag
    # KeyInstance fields.
    account_id: int                             # Spendable type field.
    masterkey_id: Optional[int]                 # Spendable type field.
    derivation_type: DerivationType             # Spendable type field.
    derivation_data2: Optional[bytes]           # Spendable type field.


class AccountTransactionOutputSpendableRowExtended(NamedTuple):
    # Standard transaction output fields.
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    script_type: ScriptType
    flags: TransactionOutputFlag
    # KeyInstance fields.
    account_id: int                             # Spendable type field.
    masterkey_id: Optional[int]                 # Spendable type field.
    derivation_type: DerivationType             # Spendable type field.
    derivation_data2: Optional[bytes]           # Spendable type field.
    # Extension fields for this type.
    tx_flags: TxFlags
    block_hash: Optional[bytes]


class TransactionOutputSpendableRow(NamedTuple):
    """
    Transaction output data with the additional key instance information required for spending it.
    """
    # Standard transaction output fields.
    tx_hash: bytes
    txo_index: int
    value: int
    keyinstance_id: Optional[int]               # Overlapping common output/spendable type field.
    script_type: ScriptType
    flags: TransactionOutputFlag
    # KeyInstance fields.
    account_id: Optional[int]                   # Spendable type field.
    masterkey_id: Optional[int]                 # Spendable type field.
    derivation_type: Optional[DerivationType]   # Spendable type field.
    derivation_data2: Optional[bytes]           # Spendable type field.

    # def to_account_row(self) -> AccountTransactionOutputSpendableRow:
    #     assert self.account_id is not None
    #     assert self.derivation_type is not None
    #     return AccountTransactionOutputSpendableRow(tx_hash=self.tx_hash,
    #           txo_index=self.txo_index,
    #         value=self.value, keyinstance_id=self.keyinstance_id, script_type=self.script_type,
    #         flags=self.flags, account_id=self.account_id, masterkey_id=self.masterkey_id,
    #         derivation_type=self.derivation_type, derivation_data2=self.derivation_data2)


# NOTE(TypeUnionsForCommonFields) NamedTuple does not support subclassing, Mypy recommends data
# classes but data classes do not do proper immutability. There's a larger problem here in that
# all our database row classes require copying of the tuple that the database query returns and
# that would ideally factor into any change in storage type. Anyway, this is the reason for these
# union types. The type checker should pick out use of any attributes that are not common to all
# included types.

# Types which have the common output fields.
TransactionOutputTypes = Union[
    TransactionOutputShortRow,
    TransactionOutputFullRow,
    TransactionOutputSpendableRow,
    AccountTransactionOutputSpendableRowExtended]
# Some lower comment.


class TransactionOutputSpendableProtocol(Protocol):
    # Standard transaction output fields.
    @property
    def tx_hash(self) -> bytes:
        ...
    @property
    def txo_index(self) -> int:
        ...
    @property
    def value(self) -> int:
        ...
    @property
    def script_type(self) -> ScriptType:
        ...
    @property
    def keyinstance_id(self) -> Optional[int]:
        ...
    @property
    def account_id(self) ->  int:
        ...
    @property
    def masterkey_id(self) ->  Optional[int]:
        ...
    @property
    def derivation_type(self) ->  DerivationType:
        ...
    @property
    def derivation_data2(self) -> Optional[bytes]:
        ...


class TransactionRow(NamedTuple):
    tx_hash: bytes
    tx_bytes: Optional[bytes]
    flags: TxFlags
    block_hash: Optional[bytes]
    block_height: int
    block_position: Optional[int]
    fee_value: Optional[int]
    description: Optional[str]
    version: Optional[int]
    locktime: Optional[int]
    date_created: int               = -1
    date_updated: int               = -1


class MerkleProofRow(NamedTuple):
    block_hash: bytes
    block_position: int
    block_height: int
    proof_data: bytes
    tx_hash: bytes


class MerkleProofUpdateRow(NamedTuple):
    block_height: int
    block_hash: bytes
    tx_hash: bytes


class TransactionProofUpdateRow(NamedTuple):
    block_hash: Optional[bytes]
    block_height: int
    block_position: Optional[int]
    tx_flags: TxFlags
    date_updated: int
    tx_hash: bytes


class TransactionProoflessRow(NamedTuple):
    tx_hash: bytes
    account_id: int


class TransactionValueRow(NamedTuple):
    tx_hash: bytes
    value: int
    flags: TxFlags
    block_hash: Optional[bytes]
    date_created: int
    date_updated: int


class TxProofData(NamedTuple):
    tx_hash: bytes
    flags: TxFlags
    block_hash: Optional[bytes]
    proof_bytes: Optional[bytes]
    tx_block_height: int
    tx_block_position: Optional[int]
    proof_block_height: int
    proof_block_position: int


class WalletBalance(NamedTuple):
    confirmed: int = 0
    unconfirmed: int = 0
    unmatured: int = 0
    allocated: int = 0

    def __add__(self, other: object) -> "WalletBalance":
        if not isinstance(other, WalletBalance):
            raise NotImplementedError
        return WalletBalance(self.confirmed + other.confirmed, self.unconfirmed + other.unconfirmed,
            self.unmatured + other.unmatured, self.allocated + other.allocated)

    def __radd__(self, other: object) -> "WalletBalance":
        if not isinstance(other, WalletBalance):
            raise NotImplementedError
        return WalletBalance(self.confirmed + other.confirmed, self.unconfirmed + other.unconfirmed,
            self.unmatured + other.unmatured, self.allocated + other.allocated)


class WalletDataRow(NamedTuple):
    key: str
    value: Any


class WalletEventInsertRow(NamedTuple):
    event_type: WalletEventType
    account_id: Optional[int]
    # NOTE(rt12): sqlite3 python module only allows custom typing if the column name is unique.
    event_flags: WalletEventFlag
    date_created: int
    date_updated: int


class WalletEventRow(NamedTuple):
    event_id: int
    event_type: WalletEventType
    account_id: Optional[int]
    # NOTE(rt12): sqlite3 python module only allows custom typing if the column name is unique.
    event_flags: WalletEventFlag
    date_created: int
    date_updated: int


class MapiBroadcastStatusFlags(IntEnum):
    ATTEMPTING = 1 << 0
    SUCCEEDED = 1 << 1


class MAPIBroadcastCallbackRow(NamedTuple):
    tx_hash: bytes
    peer_channel_id: str
    broadcast_date: str
    encrypted_private_key: bytes
    server_id: int
    status_flags: MapiBroadcastStatusFlags


class ServerPeerChannelRow(NamedTuple):
    peer_channel_id: Optional[int]
    server_id: int
    remote_channel_id: Optional[str]
    remote_url: Optional[str]
    peer_channel_flags: ServerPeerChannelFlag
    date_created: int
    date_updated: int


class ServerPeerChannelAccessTokenRow(NamedTuple):
    peer_channel_id: int
    remote_token_id: int
    token_flags: PeerChannelAccessTokenFlag
    permission_flags: int
    access_token: str


class ServerPeerChannelMessageRow(NamedTuple):
    message_id: Optional[int]
    peer_channel_id: int
    message_data: bytes
    message_flags: PeerChannelMessageFlag
    sequence: int
    date_received: int
    date_created: int
    date_updated: int


class PushDataHashRegistrationRow(NamedTuple):
    server_id: int
    # There are two kinds of registration based on key usage.
    # 1. Payment requests where an address or payment destination generated for the purpose is
    #    given out to another party.
    # 2. Where advanced users have gone to the keys tab and designated a key as forced active.
    #    this is not currently supported.
    keyinstance_id: int
    pushdata_hash: bytes
    pushdata_flags: PushDataHashRegistrationFlag
    # How many seconds from `date_created` the registration expires.
    duration_seconds: int
    # The date the server returned as the posix timestamp the registration counts from.
    date_registered: Optional[int]
    date_created: int
    date_updated: int


class PushDataMatchRow(NamedTuple):
    server_id: int
    pushdata_hash: bytes
    transaction_hash: bytes
    transaction_index: int
    block_hash: Optional[bytes]
    match_flags: PushDataMatchFlag
    date_created: int

class PushDataMatchMetadataRow(NamedTuple):
    account_id: int
    pushdata_hash: bytes
    transaction_hash: bytes
    block_hash: Optional[bytes]
