from typing import Iterator
from struct import Struct
from enum import IntEnum
from dataclasses import dataclass

class WSConstants(IntEnum):
    # 客户端发送心跳值
    WS_OP_HEARTBEAT = 2
    # 服务端返回心跳值
    WS_OP_HEARTBEAT_REPLY = 3
    # 返回消息
    WS_OP_MESSAGE = 5
    # 用户授权加入房间
    WS_OP_USER_AUTHENTICATION = 7
    # 建立连接成功，客户端接收到此信息时需要返回一个心跳包
    WS_OP_CONNECT_SUCCESS = 8
    # Header Length
    WS_PACKAGE_HEADER_TOTAL_LENGTH = 16
    WS_PACKAGE_OFFSET = 0
    WS_HEADER_OFFSET = 4
    WS_VERSION_OFFSET = 6
    WS_OPERATION_OFFSET = 8
    WS_SEQUENCE_OFFSET = 12
    WS_BODY_PROTOCOL_VERSION_NORMAL = 0
    # deflate 压缩版本
    WS_BODY_PROTOCOL_VERSION_DEFLATE = 3
    WS_HEADER_DEFAULT_VERSION = 1
    WS_HEADER_DEFAULT_OPERATION = 1
    WS_HEADER_DEFAULT_SEQUENCE = 1
    WS_AUTH_OK = 0
    WS_AUTH_TOKEN_ERROR = -101

@dataclass
class HeaderInfoItem:
    key: str
    bytes: int
    offset: int
    value: int

class HeaderInfo:
    headerLength = HeaderInfoItem("headerLen", 2, 4, 16)
    protocolVersion = HeaderInfoItem("ver", 2, 6, 1)
    operation = HeaderInfoItem("op", 4, 8, 1)
    sequenceId = HeaderInfoItem("seq", 4, 12, 1)
    itemAmount = 4 
    rawHeaderLength = itemAmount + headerLength.bytes + protocolVersion.bytes + operation.bytes + sequenceId.bytes

@dataclass
class Header:
    packLength: int
    headerLength: int
    protocolVersion: int
    operation: int
    sequenceId: int

@dataclass
class RawDanmu:
    header: Header
    body: bytes 

class Pack:
    struct = Struct(">I2H2I") # I: PackSize; 2H:HeaderLength, ProtocolVersion; 2I:Operation, SequenceId

    @staticmethod
    def pack_header(pack_size: int, opt: int) -> bytes:
        return Pack.struct.pack(pack_size, HeaderInfo.rawHeaderLength, 
                                WSConstants.WS_BODY_PROTOCOL_VERSION_DEFLATE, opt,
                                WSConstants.WS_HEADER_DEFAULT_SEQUENCE)

    @staticmethod
    def unpack_header(header: bytes) -> Header:
        pack_len, header_len, ver, opt, seq = Pack.struct.unpack_from(header)
        if header_len == HeaderInfo.rawHeaderLength:
            return Header(packLength=pack_len, headerLength=header_len,
                          protocolVersion=ver, operation=opt, 
                          sequenceId=seq)
        raise ValueError("Header Length does not equal to Raw Header Length")
    
    @staticmethod
    def pack_string(body: str, opt: int) -> bytes:
        bytes_body = body.encode("utf-8")
        pack_size = len(bytes_body) + HeaderInfo.rawHeaderLength
        header = Pack.pack_header(pack_size, opt)
        return header + bytes_body
    
    @staticmethod
    def unpack_string(packs: bytes) -> Iterator[RawDanmu]:
        pack_offset = 0
        packs_len = len(packs)
        while pack_offset != packs_len:
            header = Pack.unpack_header(packs[pack_offset:pack_offset+HeaderInfo.rawHeaderLength])
            next_pack_offset = pack_offset + header.packLength
            body = packs[pack_offset+HeaderInfo.rawHeaderLength:next_pack_offset]
            yield RawDanmu(header=header, body=body)
            pack_offset = next_pack_offset

