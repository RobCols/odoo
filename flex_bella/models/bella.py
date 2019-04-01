from odoo import api, fields, models


class BellaQuestion(models.Model):
    _name = "bella.question"
    _description = "Bella Question"

    name = fields.Char(string="Question text", translate=True)
    answer_ids = fields.One2many(
        comodel_name="bella.answer", inverse_name="question_id", string="Answers"
    )


class BellaAnswer(models.Model):
    _name = "bella.answer"
    _description = "Bella Answer"

    name = fields.Char(string="Answer Text", translate=True)
    action_id = fields.Many2one(comodel_name="bella.action", string="Action to execute")
    question_id = fields.Many2one(comodel_name="bella.question", string="Question")


class BellaAction(models.Model):
    _name = "bella.action"
    _description = "bella.action"

    name = fields.Char(string="Action Description", translate=True)
    technical_name = fields.Char(string="Technical Name")
