# ...existing imports...

class TestFightData:
    def test_initialization(self):
        """Test default initialization"""
        fight = FightData()
        assert fight.red_fighter_name == "-"
        assert fight.blue_fighter_name == "-"
        assert fight.date == "-"
        assert fight.red_fighter_total_pts == []
        assert fight.blue_fighter_total_pts == []

    def test_to_list_conversion(self):
        """Test to_list method"""
        fight = FightData(
            red_fighter_name="Red",
            blue_fighter_name="Blue",
            date="1/1/2023",
            red_fighter_total_pts=["10", "9", "10"],
            blue_fighter_total_pts=["9", "10", "9"]
        )
        list_data = fight.to_list()
        assert list_data == ["Red", "Blue", "1/1/2023", ["10", "9", "10"], ["9", "10", "9"]]

    def test_edge_cases(self):
        """Test edge cases for validation"""
        fight = FightData(
            red_fighter_name="Fighter!@#",  # Special characters
            blue_fighter_name="Blue",
            date="01/01/2023",  # Different date format
            red_fighter_total_pts=["10", "9", "10"],
            blue_fighter_total_pts=["9", "10", "9"]
        )
        assert fight.validate()  # Should accept special characters in names

    def test_none_values(self):
        """Test handling of None values"""
        fight = FightData(
            red_fighter_name=None,  # Should use default "-"
            blue_fighter_name="Blue",
            date="1/1/2023",
            red_fighter_total_pts=["10", "9", "10"],
            blue_fighter_total_pts=["9", "10", "9"]
        )
        assert not fight.validate()  # Should fail validation

    # ...existing test methods...
