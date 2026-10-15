import pandas as pd
import plotly.express as px


class ChartTool:
    """Prepare SQL results for tabular and chart visualization."""

    def result_to_dataframe(self, result: list) -> pd.DataFrame:
        """Convert SQLite result rows into a pandas DataFrame."""
        return pd.DataFrame(result)

    def should_chart(self, df: pd.DataFrame) -> bool:
        """
        Decide whether the result is suitable for a chart.

        Charts are useful when:
        - There are at least 2 rows.
        - There are at least 2 columns.
        - At least one column is numeric.
        """
        if df.empty:
            return False

        if len(df) < 2:
            return False

        if len(df.columns) < 2:
            return False

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns

        return len(numeric_columns) > 0

    def _select_x_column(self, df: pd.DataFrame, numeric_columns: list[str]):
        """Select the most suitable categorical column for the X-axis."""

        categorical_columns = [
            column
            for column in df.columns
            if column not in numeric_columns
        ]

        if categorical_columns:
            return categorical_columns[0]

        # If all columns are numeric, use the first column.
        return df.columns[0]

    def _select_y_column(self, df: pd.DataFrame, numeric_columns: list[str]):
        """
        Select the most meaningful numeric column for the Y-axis.

        Prefer measurement/metric columns over identifiers.
        """

        metric_keywords = [
            "total",
            "spent",
            "spending",
            "amount",
            "revenue",
            "sales",
            "price",
            "count",
            "number",
            "quantity",
            "average",
            "avg",
            "sum",
            "value",
            "score",
            "rate",
            "percentage",
            "percent",
        ]

        id_keywords = [
            "id",
            "identifier",
        ]

        # First pass: strongly prefer metric-like columns.
        for column in numeric_columns:
            column_lower = str(column).lower()

            if any(
                keyword in column_lower
                for keyword in metric_keywords
            ):
                return column

        # Second pass: avoid identifier columns when possible.
        non_id_numeric_columns = [
            column
            for column in numeric_columns
            if not any(
                keyword in str(column).lower()
                for keyword in id_keywords
            )
        ]

        if non_id_numeric_columns:
            return non_id_numeric_columns[0]

        # Final fallback.
        return numeric_columns[0]

    def create_chart(self, df: pd.DataFrame):
        """Create a Plotly chart from a tabular SQL result."""

        if not self.should_chart(df):
            return None

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        x_column = self._select_x_column(
            df,
            numeric_columns
        )

        y_column = self._select_y_column(
            df,
            numeric_columns
        )

        figure = px.bar(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}",
        )

        return figure