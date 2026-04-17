from sqlalchemy import select
from app.models.catalog import Product, Quarry
from app.models.process import ProcessInput, ProcessOutput
from app.repositories.process_repository import ProcessRepository
from app.schemas.plc_contract import (
    PlcContractContext,
    PlcContractInputItem,
    PlcContractLineSnapshot,
    PlcContractOutputItem,
)
from app.services.plc_mock_state import plc_mock_state


class PlcContractService:
    def __init__(self, db):
        self.db = db
        self.process_repository = ProcessRepository(db)

    def get_line_snapshot(self, line: int) -> PlcContractLineSnapshot:
        process = self.process_repository.get_active_by_line(line)
        mock_context = plc_mock_state['context']

        inputs: list[PlcContractInputItem] = []
        outputs: list[PlcContractOutputItem] = []

        if process:
            input_rows = self.db.execute(
                select(ProcessInput, Quarry.name)
                .join(Quarry, Quarry.id == ProcessInput.quarry_id)
                .where(ProcessInput.process_id == process.id)
                .order_by(ProcessInput.input_order.asc())
            ).all()
            for process_input, quarry_name in input_rows:
                inputs.append(
                    PlcContractInputItem(
                        quarry=quarry_name,
                        hopper_code=process_input.hopper_code,
                        blend_target_pct=float(process_input.blend_target_pct) if process_input.blend_target_pct is not None else None,
                    )
                )

            output_rows = self.db.execute(
                select(ProcessOutput, Product.name)
                .join(Product, Product.id == ProcessOutput.product_id, isouter=True)
                .where(ProcessOutput.process_id == process.id)
                .order_by(ProcessOutput.id.asc())
            ).all()
            for process_output, product_name in output_rows:
                outputs.append(
                    PlcContractOutputItem(
                        output_code=process_output.output_code,
                        classification=process_output.classification,
                        product=product_name,
                    )
                )

        context = PlcContractContext(
            process_code=process.code if process else None,
            process_enabled=bool(process),
            line=line,
            mode=process.mode if process else mock_context.get('mode'),
            mode_blend=bool(process and process.mode == 'blend'),
            blend_target_a_pct=mock_context.get('blend_target_a_pct'),
            blend_target_b_pct=mock_context.get('blend_target_b_pct'),
            reset_partials_requested=bool(mock_context.get('reset_partials_requested', False)),
            inputs=inputs,
            outputs=outputs,
        )
        return PlcContractLineSnapshot(
            line=line,
            has_active_process=bool(process),
            context=context,
        )
