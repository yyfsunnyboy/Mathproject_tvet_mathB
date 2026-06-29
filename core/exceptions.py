class RetryableSamplingError(ValueError):
    """Exception raised when random parameters cannot satisfy mathematical constraints, 
    but changing the random seed can resolve the issue."""
    def __init__(
        self,
        msg: str,
        *,
        total_students: int | None = None,
        class_count: int | None = None,
        minimum_total: int | None = None,
        operation: str | None = None,
    ) -> None:
        super().__init__(msg)
        self.total_students = total_students
        self.class_count = class_count
        self.minimum_total = minimum_total
        self.operation = operation
