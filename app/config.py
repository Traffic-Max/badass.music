import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = str(os.environ.get('DATABASE_URL'))


all_possible_meta_fields = [
        "TIT2", "TPE1", "TRCK", "TALB", "TDRC", "TCON", "TSSE", "TIT3",
        "COMM", "TCOP", "TOPE", "TCOM", "TPOS", "TBPM", "TKEY", "TLAN",
        "WPAY", "WOAR", "AENC", "APIC", "ASPI", "COMM", "COMR", "ENCR",
        "EQU2", "ETCO", "GEOB", "GRID", "LINK", "MCDI", "MLLT", "OWNE",
        "PRIV", "PCNT", "POPM", "POSS", "RBUF", "RVA2", "RVRB", "SEEK",
        "SYLT", "SYTC", "TDEN", "TDLY", "TDOR", "TDRL", "TDTG", "TENC",
        "TEXT", "TFLT", "TIPL", "TIT1", "TKEY", "TLAN", "TLEN", "TMCL",
        "TMED", "TMOO", "TOAL", "TOFN", "TOLY", "TOPE", "TORY", "TOWN",
        "TPE2", "TPE3", "TPE4", "TPRO", "TPUB", "TRSN", "TRSO", "TSRC",
        "TSSE", "TSST", "TXXX", "UFID", "USER", "USLT", "WCOM", "WCOP",
        "WOAF", "WOAS", "WORS", "WPUB", "WXXX", "TDAT", "TIME", "TORY",
        "TRDA", "TSIZ", "TYER", "IPLS", "RVAD", "EQUA", "GEOB", "RVRB",
        "TDES", "TGID", "TSSO", "WFED", "PCST"
    ]
