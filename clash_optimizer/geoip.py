import geoip2.database
from geoip2.errors import AddressNotFoundError

class GeoIPClassifier:
    def __init__(self, mmdb_path: str):
        self.reader = geoip2.database.Reader(mmdb_path)

    def get_country_code(self, ip: str) -> str:
        try:
            response = self.reader.country(ip)
            code = response.country.iso_code
            return code if code else "ZZ"
        except AddressNotFoundError:
            print(f"⚠️ IP not found in GeoIP database: {ip}")
            return "ZZ"
        except Exception as e:
            print(f"❌ GeoIP lookup failed for {ip}: {e}")
            return "ZZ"
