import ast
import operator

from app.skills.base import Skill


class CalculatorSkill(Skill):

    name = "calculator"

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def execute(self, action, parameters):

        if action != "calculate":
            return {
                "success": False,
                "message": "Unknown calculator action."
            }

        expression = parameters.get("expression", "").strip()

        if not expression:
            return {
                "success": False,
                "message": "No expression provided."
            }

        try:
            result = self._calculate(expression)

            return {
                "success": True,
                "message": str(result),
                "data": {
                    "expression": expression,
                    "result": result,
                }
            }

        except Exception:
            return {
                "success": False,
                "message": "I couldn't calculate that expression."
            }

    def _calculate(self, expression):

        tree = ast.parse(expression, mode="eval")

        return self._evaluate(tree.body)

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Unsupported value")

        if isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError("Unsupported operator")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            return self.OPERATORS[operator_type](left, right)

        if isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError("Unsupported operator")

            value = self._evaluate(node.operand)

            return self.OPERATORS[operator_type](value)

        raise ValueError("Unsupported expression")