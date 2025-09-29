from enum import Enum


class Data(Enum):
    LOCATION = "location"
    ANALYTICS = "analytics"
    COARSE_LOCATION = "coarse_location"
    CITY = "city"
    COUNTRY = "country"
    REGION = "region"
    FINE_LOCATION = "fine_location"
    GPS = "gps"
    INTERNET_ACTIVITY = "internet_activity"
    APPLICATION = "application"  # application info
    BROWSING = "browsing"
    HTTP = "http"
    ACCOUNT = "account"
    USAGE_STATISTICS = "usage_statistics"
    LOG = "log"
    STACK = "stack"
    ADVERTISING = "advertising"
    ADVERTISING_STATISTICS = "advertising_statistics"
    GOVERNMENT_IDENTIFIER = "government_identifier"
    ID_CARD = "id_card"  # SSN
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    CONTACT_INFORMATION = "contact_information"
    ADDRESS = "address"
    EMAIL = "email"
    PERSONAL_INFO = "personal_info"
    PERSONAL_NAME = "personal_name"
    PHONE_NUMBER = "phone_number"
    SOFTWARE_IDENTIFIER = "software_identifier"
    IP_ADDRESS = "ip_address"
    WIFI = "wifi"
    ANDROID_ID = "android_id"
    GSF_ID = "gsf_id"
    ADVERTISING_ID = "advertising_id"
    COOKIE = "cookie"
    OS = "os"  # operating system
    HARDWARE_IDENTIFIER = "hardware_identifier"
    MAC_ADDRESS = "mac_address"
    IMEI = "imei"
    SIM_SERIAL_NUMBER = "sim_serial_number"
    SERIAL_NUMBER = "serial_number"
    DEVICE = "device"
    PROTECTED_INFORMATION = "protected_information"
    GENDER = "gender"
    RACE = "race"
    DATE_OF_BIRTH = "date_of_birth"
    AGE = "age"
    BIOMETRIC_INFORMATION = "biometric_information"
    VOICEPRINT = "voiceprint"
    FINGERPRINT = "fingerprint"
    NON_PERSONAL_INFO = "non_personal_info"
    SECURITY = "security"
    ENCRYPTION = "encryption"
    ANONYMOUS = "anonymous"  # deidentified
    PERMISSION = "permission"
    ANDROID_PERMISSION = "android_permission"
    TRANSFORMED_INFORMATION = "transformed_information"
    AGGRAGATE = "aggregate"
    PSEUDONYMOUS = "pseudonymous"
    ANY = "any"
    UUID = "uuid"
    SENSITIVE_INFO = 'sensitive_info'

    def __str__(self):
        return f"Data('{self.name}')"

    def __eq__(self, other):
        if not isinstance(other, Data):
            return False
        return self.name == other.name

    def __ne__(self, other):
        if isinstance(other, Data):
            return self.name != other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def check_value_in_enum(value: str):
        for item in Data:
            if item.value == value:
                return True
        return False

    @staticmethod
    def find_most_similar(value: str):
        sorted_items = sorted([item for item in Data], key=lambda x: (-len(x.value), x.value))
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
