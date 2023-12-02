import ast
import inspect

from sqlalchemy.orm import Session
from py_frm.model import model_for


def to_sqlalchemy_query(function, session: Session):
    source_code = inspect.getsource(function)
    parsed_code = ast.parse(source_code)

    def extract_info(node):
        if isinstance(node, ast.FunctionDef):
            for statement in node.body:
                if isinstance(statement, ast.Return) and isinstance(
                    statement.value, ast.GeneratorExp
                ):
                    return parse_generator_exp(statement.value)
        raise ValueError("No valid generator expression found in function.")

    def parse_generator_exp(gen_exp):
        select_clause = []
        conditions = []
        var_to_model_map = {}

        # Mapping each iterator variable to its corresponding model
        for gen in gen_exp.generators:
            var_to_model_map[gen.target.id] = model_for(gen.iter.id)

        # Constructing the SELECT clause based on the structure of gen_exp.elt
        if isinstance(gen_exp.elt, ast.Tuple):
            for elt in gen_exp.elt.elts:
                if isinstance(elt, ast.Attribute) and elt.value.id in var_to_model_map:
                    model_class = var_to_model_map[elt.value.id]
                    select_clause.append(getattr(model_class, elt.attr))
        else:
            if (
                isinstance(gen_exp.elt, ast.Attribute)
                and gen_exp.elt.value.id in var_to_model_map
            ):
                model_class = var_to_model_map[gen_exp.elt.value.id]
                select_clause.append(getattr(model_class, gen_exp.elt.attr))

        # Constructing the WHERE clause for conditions
        for gen in gen_exp.generators:
            for if_clause in gen.ifs:
                if isinstance(if_clause, ast.Compare) and isinstance(
                    if_clause.ops[0], ast.Eq
                ):
                    left_var, left_attr = if_clause.left.value.id, if_clause.left.attr
                    right_var, right_attr = (
                        if_clause.comparators[0].value.id,
                        if_clause.comparators[0].attr,
                    )
                    left_model = var_to_model_map[left_var]
                    right_model = var_to_model_map[right_var]
                    conditions.append(
                        getattr(left_model, left_attr)
                        == getattr(right_model, right_attr)
                    )

        query = session.query(*select_clause)
        for condition in conditions:
            query = query.filter(condition)

        return query

    return extract_info(parsed_code.body[0])
