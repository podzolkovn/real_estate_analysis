# from decimal import Decimal
# from uuid import uuid4
#
# import pytest
#
# from app.core.enums import StatusEnum
# from app.domain.template_schema import OrderSchema
# from app.domain.template_schema.service import OrderTemplateService
#
#
# class TestOrderTotalCalculation:
#     service: OrderTemplateService = OrderTemplateService()
#
#     @pytest.mark.asyncio(loop_scope="session")
#     async def test_calculate_total(self):
#         order = OrderSchema(
#             id=uuid4(),
#             name="test",
#             status=StatusEnum.CONFIRMED,
#             total_price=Decimal("10.00")
#         )
#         calc_total = await self.service.fake_calculate_total(order)
#         assert calc_total == order.total_price
