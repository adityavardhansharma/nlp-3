import configparser, os

_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.path.dirname(__file__), "..", "config.ini"))
conf = _cfg["DEFAULT"]

JSONL_PATH         = conf["JSONL_PATH"]
CHROMA_DIR         = conf["CHROMA_DIR"]
BI_ENCODER_MODEL   = conf["BI_ENCODER_MODEL"]
PARAPHRASE_MODEL   = conf["PARAPHRASE_MODEL"]
TOP_K              = _cfg.getint("DEFAULT", "TOP_K")
FIDELITY_THRESH    = _cfg.getfloat("DEFAULT","FIDELITY_THRESH")
