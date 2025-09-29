from enum import Enum


class Entity(Enum):
    WIRELESS_CARRIER = "wireless_carrier"
    SUBSPLASH = "subsplash"
    HEYSTACK = "heystack"
    UNSPECIFIED = "unspecified"
    THIRD_PARTIES = "third_parties"
    GOOGLE = "google"
    ANDROID = "android"
    FIREBASE = "firebase"
    YOUTUBE = "youtube"
    ADMOB = "admob"
    CRASHLYTICS = "crashlytics"
    GOOGLE_ADS = "google_ads"
    GOOGLE_ANALYTICS = "google_analytics"
    GOOGLE_CLOUD = "google_cloud"
    GOOGLE_MAPS = "google_maps"
    GOOGLE_PLAY = "google_play"
    GOOGLE_AUTH = "google_auth"
    # GEMINI = "gemini"
    GMAIL = "gmail"
    FACEBOOK = "facebook"
    META = "meta"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    OCULUS = "oculus"
    MESSENGER = "messenger"
    FACEBOOK_ADS = "facebook_ads"
    FACEBOOK_GAMING = "facebook_gaming"
    # LLAMA = "llama"
    AMAZON = "amazon"
    AWS = "aws"
    # ATTRIBUTION = "attribution"
    ALEXA = "alexa"
    AMAZON_PRIME = "amazon_prime"
    KINDLE = "kindle"
    AMAZON_MUSIC = "amazon_music"
    AMAZON_VIDEO = "amazon_video"
    APPLE = "apple"
    APPSTORE = "appstore"
    ICLOUD = "icloud"
    ITUNES = "itunes"
    APPLE_MUSIC = "apple_music"
    APPLE_TV = "apple_tv"
    FACETIME = "facetime"
    SIRI = "siri"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
    AZURE = "azure"
    XBOX = "xbox"
    OUTLOOK = "outlook"
    TEAMS = "teams"
    ONEDRIVE = "onedrive"
    TWITTER = "twitter"
    TWEEPY = "tweepy"
    TWEETDECK = "tweetdeck"
    # PERISCOPE = "periscope"
    # VINE = "vine"
    SNAPCHAT = "snapchat"
    SNAP = "snap"
    # SPECTACLES = "spectacles"
    BITMOJI = "bitmoji"
    SNAP_MAP = "snap_map"
    UNITY = "unity"
    UNITY_ADS = "unity_ads"
    # UNITY_PLAYABLES = "unity_playables"
    MULTIPLAYER = "multiplayer"
    VUNGLE = "vungle"
    VUNGLE_ADS = "vungle_ads"
    YAHOO = "yahoo"
    YAHOO_MAIL = "yahoo_mail"
    YAHOO_FINANCE = "yahoo_finance"
    YAHOO_SPORTS = "yahoo_sports"
    ADCOLONY = "adcolony"
    ADCOLONY_ADS = "adcolony_ads"
    AIRBNB = "airbnb"
    AIRCOVER = "aircover"
    EXPERIENCES = "experiences"
    HOMES = "homes"
    APPSFLYER = "appsflyer"
    APPSFLYER_ANALYTICS = "appsflyer_analytics"
    ADJUST = "adjust"
    COMCAST = "comcast"
    XFINITY = "xfinity"
    # PEACOCK = "peacock"
    COMCAST_BUSINESS = "comcast_business"
    DISNEY = "disney"
    DISNEY_PLUS = "disney_plus"
    PIXAR = "pixar"
    MARVEL = "marvel"
    EBAY = "ebay"
    EBAY_AUCTIONS = "ebay_auctions"
    EBAY_SELLERS = "ebay_sellers"
    EBAY_STORE = "ebay_store"
    FLUCT = "fluct"
    IAB = "iab"
    INMOBI = "inmobi"
    INMOBI_ADS = "inmobi_ads"
    INMOBI_ANALYTICS = "inmobi_analytics"
    # INMOBI_AUDIENCE = "inmobi_audience"
    ORACLE = "oracle"
    MOAT = "moat"
    ORACLE_CLOUD = "oracle_cloud"
    ORACLE_DATABASE = "oracle_database"
    ORACLE_ERP = "oracle_erp"
    ORACLE_HCM = "oracle_hcm"
    ORACLE_CX = "oracle_cx"
    ORACLE_SCM = "oracle_scm"
    ORACLE_ANALYTICS = "oracle_analytics"
    APPLOVIN = "applovin"
    MOPUB = "mopub"
    MYTARGET = "mytarget"
    MYTARGET_ADS = "mytarget_ads"
    MYTARGET_AUDIENCE = "mytarget_audience"
    PINTEREST = "pinterest"
    PINTEREST_ADS = "pinterest_ads"
    PINTEREST_ANALYTICS = "pinterest_analytics"
    ROKU = "roku"
    # ROKU_CHANNEL = "roku_channel"
    ROKU_ADS = "roku_ads"
    TAPJOY = "tapjoy"
    TAPJOY_ADS = "tapjoy_ads"
    # TAPJOY_ANALYTICS = "tapjoy_analytics"
    PAYPAL = "paypal"
    VENMO = "venmo"
    BRAINTREE = "braintree"
    XOOM = "xoom"
    SQUARE = "square"
    CASHAPP = "cashapp"
    TOCK = "tock"
    AFTERPAY = "afterpay"
    ADOBE = "adobe"
    PHOTOSHOP = "photoshop"
    ACROBAT = "acrobat"
    ILLUSTRATOR = "illustrator"
    STRIPE = "stripe"
    # ATLAS = "atlas"
    # SIGMA = "sigma"
    # RADAR = "radar"
    BYTEDANCE = "bytedance"
    # HUOSHAN = "huoshan"
    TIKTOK = "tiktok"
    XIGUA = "xigua"
    DOUBAO = "doubao"
    TOUTIAO = "toutiao"
    # PIPIXIA = "pipixia"
    # DONGCHEDI = "dongchedi"
    ALIBABA = "alibaba"
    TAOBAO = "taobao"
    ALIPAY = "alipay"
    ALICLOUD = "alicloud"
    TMALL = "tmall"
    ALIEXPRESS = "aliexpress"
    LAZADA = "lazada"
    # TONGYI = "tongyi"
    ELEME = "eleme"
    XIANYU = "xianyu"
    # KOUBEI = "koubei"
    # KOUBEI_MERCHANT = "koubei_merchant"
    BAIDU = "baidu"
    BAIDU_MAP = "baidu_map"
    BAIDU_SEARCH = "baidu_search"
    HUAWEI = "huawei"
    HUAWEI_CLOUD = "huawei_cloud"
    HUAWEI_MOBILE = "huawei_mobile"
    HARMONYOS = "harmonyos"
    # HISILICON = "hisilicon"
    SANKUAI = "sankuai"
    MEITUAN = "meituan"
    DIANPING = "dianping"
    MEIZU = "meizu"
    # FLYME = "flyme"
    TENCENT = "tencent"
    IHOC = "ihoc"
    WECHAT = "wechat"
    QQMUSIC = "qqmusic"
    TENCENTVIDEO = "tencentvideo"
    TENCENTCLOUD = "tencentcloud"
    TENCENTGAMES = "tencentgames"
    UNIONPAY = "unionpay"
    XIAOMI = "xiaomi"
    MIUI = "miui"
    XIAOMI_STORE = "xiaomi_store"
    # ZTUNI = "ztuni"
    SOGOU = "sogou"
    # TUGELE = "tugele"
    # SOGOU_INPUT = "sogou_input"
    SOHU = "sohu"
    SOHU_VIDEO = "sohu_video"
    SOHU_NEWS = "sohu_news"
    BBK = "bbk"
    VIVO = "vivo"
    OPPO = "oppo"
    # HEYTAP = "heytap"
    QIHOO360 = "qihoo360"
    IFLYTEK = "iflytek"
    FENGMAP = "fengmap"
    CMIC = "cmic"
    CHINATELECOM = "chinatelecom"
    SINA = "sina"
    WE = "we"
    ADVERTISER = "advertiser"
    ANALYTICS = "analytics"
    SOCIAL_MEDIA = "social_media"
    CONTENT_PROVIDER = "content_provider"
    AUTH_PROVIDER = "auth_provider"
    EMAIL_PROVIDER = "email_provider"
    # added 20241229
    REGULATORY = "regulatory"
    NETSCAPE = "netscape"
    REDORBIT = "redorbit"
    AOL = "aol"
    MAPQUEST = "mapquest"
    VERIZON = "verizon"
    DOUBLECLICK = "doubleclick"
    HONDA = "honda"
    HONDA_MOTOR = "honda_motor"
    MARKETER = 'marketer'
    SERVICE_COMPANY = 'service_company'
    FINANCIAL_SERVICE = 'financial_service'
    ISP = 'isp'
    BANK = 'bank'
    AUTOMOBILE_DEALER = 'automobile_dealer'
    NORTHERN_TOOL = 'northern_tool'
    ATT = 'att'
    STARBUCKS = 'starbucks'
    SPRINT = 'sprint'
    T_MOBILE = 't_mobile'
    # jr_electronics
    JR_ELECTRONICS = 'jr_electronics'
    OFFICEMAX = 'officemax'
    # eddie_bauer
    EDDIE_BAUER = 'eddie_bauer'
    VENDOR = 'vendor'
    CHINA = 'china'
    USA = 'usa'
    EUROPE = 'europe'

    def __str__(self):
        return f"Entity('{self.name}')"

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.name == other.name

    def __ne__(self, other):
        if isinstance(other, Entity):
            return self.name != other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def check_value_in_enum(value: str):
        for item in Entity:
            if item.value == value:
                return True
        return False

    @staticmethod
    def find_most_similar(value: str):
        sorted_items = sorted([item for item in Entity], key=lambda x: (-len(x.value), x.value))
        min_diff = float('inf')
        most_similar_item = None

        for item in sorted_items:
            len_diff = abs(len(item.value) - len(value))
            char_diff = sum(1 for c1, c2 in zip(item.value, value) if c1 != c2)

            diff = len_diff + char_diff
            if diff < min_diff:
                min_diff = diff
                most_similar_item = item

        return most_similar_item
