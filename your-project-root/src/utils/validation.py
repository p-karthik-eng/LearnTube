class ValidationUtils:
    @staticmethod
    def validate_json_structure(data: dict, required_keys: list) -> bool:
        """Validate JSON structure has required keys"""
        return all(key in data for key in required_keys)
