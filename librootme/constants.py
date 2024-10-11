from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Literal, TypeAlias

from .types import DifficultyStr
from .utils import strip_tags

LanguageCode: TypeAlias = Literal["fr", "en", "de", "es", "ru", "zh"]
AccountTypeCode: TypeAlias = Literal[
    "0minirezo",
    "5pre",
    "1comite",
    "6forum",
    "nouveau",
    "aconfirmer",
    "5cheater",
    "5leaker",
    "5poubelle",
    "5banned",
]
RankCode: TypeAlias = Literal[
    "visitor", "curious", "trainee", "insider", "enthusiast", "hacker", "elite", "legend"
]
RelType: TypeAlias = Literal["previous", "next"]

LANGUAGE_NAMES: dict[LanguageCode, str] = {
    "fr": "French",
    "en": "English",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "zh": "Chinese",
}
ACCOUNT_TYPE_COLORS: dict[AccountTypeCode, str] = {
    "0minirezo": "#767676",
    "5pre": "#DE2B0F",
    "1comite": "#DE770F",
    "6forum": "#00CC00",
}


class Language(StrEnum):
    FR = "fr"
    EN = "en"
    DE = "de"
    ES = "es"
    RU = "ru"
    ZH = "zh"

    @property
    def full_name(self) -> str:
        return LANGUAGE_NAMES[self.value]


class AccountType(StrEnum):
    ADMIN = "0minirezo"
    PREMIUM = "5pre"
    REDACTOR = "1comite"
    VISITOR = "6forum"
    NEW = "nouveau"
    UNCONFIRMED = "aconfirmer"
    CHEATER = "5cheater"
    LEAKER = "5leaker"
    TRASH = "5poubelle"
    BANNED = "5banned"

    def __str__(self) -> str:
        return self.name.capitalize()

    @property
    def is_banned(self) -> bool:
        return self in {
            AccountType.CHEATER,
            AccountType.LEAKER,
            AccountType.TRASH,
            AccountType.BANNED,
        }

    @property
    def color(self, default: str = "#CCCCCC") -> str:
        return ACCOUNT_TYPE_COLORS.get(self.value, default)


class Rank(StrEnum):
    VISITOR = "visitor"
    CURIOUS = "curious"
    TRAINEE = "trainee"
    INSIDER = "insider"
    ENTHUSIAST = "enthusiast"
    HACKER = "hacker"
    ELITE = "elite"
    LEGEND = "legend"

    def __str__(self) -> str:
        return self.name.capitalize()


class Category(IntEnum):
    WEB_CLIENT = 16
    PROGRAMMING = 17
    CRYPTANALYSIS = 18
    STEGANOGRAPHY = 67
    WEB_SERVER = 68
    CRACKING = 69
    REALIST = 70
    NETWORK = 182
    APP_SCRIPT = 189
    APP_SYSTEM = 203
    FORENSIC = 208

    def get_name(self, lang: Language = Language.EN) -> str:
        return CATEGORY_NAMES[lang][self]


class CategoryLocalized(IntEnum):
    FR_APP_SCRIPT = 189
    FR_APP_SYSTEM = 203
    FR_CRACKING = 69
    FR_CRYPTANALYSIS = 18
    FR_FORENSIC = 208
    FR_PROGRAMMING = 17
    FR_REALIST = 70
    FR_NETWORK = 182
    FR_STEGANOGRAPHY = 67
    FR_WEB_CLIENT = 16
    FR_WEB_SERVER = 68

    EN_APP_SCRIPT = 191
    EN_APP_SYSTEM = 204
    EN_CRACKING = 158
    EN_CRYPTANALYSIS = 160
    EN_FORENSIC = 209
    EN_PROGRAMMING = 159
    EN_REALIST = 157
    EN_NETWORK = 183
    EN_STEGANOGRAPHY = 156
    EN_WEB_CLIENT = 155
    EN_WEB_SERVER = 154

    DE_APP_SCRIPT = 217
    DE_APP_SYSTEM = 218
    DE_CRACKING = 228
    DE_CRYPTANALYSIS = 229
    DE_FORENSIC = 230
    DE_PROGRAMMING = 231
    DE_REALIST = 235
    DE_NETWORK = 232
    DE_STEGANOGRAPHY = 236
    DE_WEB_CLIENT = 234
    DE_WEB_SERVER = 233

    ES_APP_SCRIPT = 251
    ES_APP_SYSTEM = 252
    ES_CRACKING = 253
    ES_CRYPTANALYSIS = 254
    ES_FORENSIC = 255
    ES_PROGRAMMING = 256
    ES_REALIST = 257
    ES_NETWORK = 258
    ES_STEGANOGRAPHY = 259
    ES_WEB_CLIENT = 260
    ES_WEB_SERVER = 261

    RU_APP_SCRIPT = 327
    RU_APP_SYSTEM = 329
    RU_CRACKING = 323
    RU_CRYPTANALYSIS = 325
    RU_FORENSIC = 330
    RU_PROGRAMMING = 324
    RU_REALIST = 322
    RU_NETWORK = 326
    RU_STEGANOGRAPHY = 321
    RU_WEB_CLIENT = 320
    RU_WEB_SERVER = 319

    ZH_APP_SCRIPT = 371
    ZH_APP_SYSTEM = 376
    ZH_CRACKING = 359
    ZH_CRYPTANALYSIS = 361
    ZH_FORENSIC = 377
    ZH_PROGRAMMING = 360
    ZH_REALIST = 358
    ZH_NETWORK = 370
    ZH_STEGANOGRAPHY = 357
    ZH_WEB_CLIENT = 356
    ZH_WEB_SERVER = 355

    @property
    def lang(self) -> Language:
        return Language[self.name.split("_", 1)[0]]

    @property
    def category(self) -> Category:
        return Category[self.name.split("_", 1)[1]]

    def __str__(self) -> str:
        return self.category.get_name(self.lang)


CATEGORY_NAMES: dict[Language, dict[Category, str]] = {
    Language.FR: {
        Category.WEB_CLIENT: "Web - Client",
        Category.PROGRAMMING: "Programmation",
        Category.CRYPTANALYSIS: "Cryptanalyse",
        Category.STEGANOGRAPHY: "Stéganographie",
        Category.WEB_SERVER: "Web - Serveur",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Réaliste",
        Category.NETWORK: "Réseau",
        Category.APP_SCRIPT: "App - Script",
        Category.APP_SYSTEM: "App - Système",
        Category.FORENSIC: "Forensic",
    },
    Language.EN: {
        Category.WEB_CLIENT: "Web - Client",
        Category.PROGRAMMING: "Programming",
        Category.CRYPTANALYSIS: "Cryptanalysis",
        Category.STEGANOGRAPHY: "Steganography",
        Category.WEB_SERVER: "Web - Server",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Realist",
        Category.NETWORK: "Network",
        Category.APP_SCRIPT: "App - Script",
        Category.APP_SYSTEM: "App - System",
        Category.FORENSIC: "Forensic",
    },
    Language.DE: {
        Category.WEB_CLIENT: "Web - Kunde",
        Category.PROGRAMMING: "Programmierung",
        Category.CRYPTANALYSIS: "Kryptoanalyse",
        Category.STEGANOGRAPHY: "Steganografie",
        Category.WEB_SERVER: "Web - Server",
        Category.CRACKING: "Knacken",
        Category.REALIST: "Realist",
        Category.NETWORK: "Netzwerk",
        Category.APP_SCRIPT: "App - Skript",
        Category.APP_SYSTEM: "Anwendung - System",
        Category.FORENSIC: "Forensische",
    },
    Language.ES: {
        Category.WEB_CLIENT: "Web - Cliente",
        Category.PROGRAMMING: "Programación",
        Category.CRYPTANALYSIS: "Criptoanálisis",
        Category.STEGANOGRAPHY: "Esteganografía",
        Category.WEB_SERVER: "Web - Servidor",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Realista",
        Category.NETWORK: "Red",
        Category.APP_SCRIPT: "Aplicación - Guión",
        Category.APP_SYSTEM: "Aplicación - Sistema",
        Category.FORENSIC: "Forense",
    },
    Language.RU: {
        Category.WEB_CLIENT: "Веб - Клиент",
        Category.PROGRAMMING: "Программирование",
        Category.CRYPTANALYSIS: "Криптоанализ",
        Category.STEGANOGRAPHY: "Стеганография",
        Category.WEB_SERVER: "Веб - сервер",
        Category.CRACKING: "Взлом",
        Category.REALIST: "Реалист",
        Category.NETWORK: "Сеть",
        Category.APP_SCRIPT: "App - Сценарий",
        Category.APP_SYSTEM: "Приложение - Система",
        Category.FORENSIC: "Судебная экспертиза",
    },
    Language.ZH: {
        Category.WEB_CLIENT: "网络 - 客户端",
        Category.PROGRAMMING: "编程",
        Category.CRYPTANALYSIS: "密码分析",
        Category.STEGANOGRAPHY: "隐写术",
        Category.WEB_SERVER: "网络 - 服务器",
        Category.CRACKING: "裂缝",
        Category.REALIST: "现实主义者",
        Category.NETWORK: "网络",
        Category.APP_SCRIPT: "应用程序 - 脚本",
        Category.APP_SYSTEM: "应用程序 - 系统",
        Category.FORENSIC: "法医",
    },
}


class Difficulty(StrEnum):
    VERY_EASY = "Très facile"
    EASY = "Facile"
    MEDIUM = "Moyen"
    HARD = "Difficile"
    VERY_HARD = "Très difficile"

    @classmethod
    def from_str(cls, value: DifficultyStr) -> Difficulty:
        value_str = strip_tags(value).lower()
        for diff_name in DIFFICULTY_NAMES.values():
            for diff, name in diff_name.items():
                if value_str == name.lower():
                    return diff
        return cls(value_str)

    def localized_name(self, lang: Language | LanguageCode) -> str:
        lang = Language(lang)
        if lang not in DIFFICULTY_NAMES:
            lang = Language.EN
        return DIFFICULTY_NAMES[lang][self]


DIFFICULTY_NAMES: dict[Language, dict[Difficulty, str]] = {
    Language.FR: {
        Difficulty.VERY_EASY: "Très facile",
        Difficulty.EASY: "Facile",
        Difficulty.MEDIUM: "Moyen",
        Difficulty.HARD: "Difficile",
        Difficulty.VERY_HARD: "Très difficile",
    },
    Language.EN: {
        Difficulty.VERY_EASY: "Very easy",
        Difficulty.EASY: "Easy",
        Difficulty.MEDIUM: "Medium",
        Difficulty.HARD: "Hard",
        Difficulty.VERY_HARD: "Very hard",
    },
    Language.DE: {
        Difficulty.VERY_EASY: "Sehr einfach",
        Difficulty.EASY: "Einfach",
        Difficulty.MEDIUM: "Mittel",
        Difficulty.HARD: "Schwer",
        Difficulty.VERY_HARD: "Sehr Schwer",
    },
    # Other languages haven't been translated on the website or API,
    # they use the French names wrapped in a <span lang="fr"> tag
}


class Rel(StrEnum):
    PREV = "previous"
    NEXT = "next"
