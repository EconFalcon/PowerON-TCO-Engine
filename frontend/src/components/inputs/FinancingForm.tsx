import { useInputStore } from '../../store/useInputStore';
import { LabeledField, Input, SectionTitle } from '../common';

export default function FinancingForm() {
  const { loan, setLoan, lease, setLease, discount_rate } = useInputStore();
  const setDiscountRate = (v: number) => useInputStore.setState({ discount_rate: v });

  return (
    <div>
      <SectionTitle>Loan Parameters (Scenarios 2 & 3)</SectionTitle>

      <LabeledField label="Interest Rate" hint="%">
        <Input type="number" min={0} max={100} step={0.1} value={(loan.interest_rate * 100).toFixed(1)}
          onChange={(e) => setLoan({ interest_rate: +e.target.value / 100 })} />
      </LabeledField>

      <div className="grid grid-cols-2 gap-3">
        <LabeledField label="Down Payment" hint="%">
          <Input type="number" min={0} max={100} step={1} value={(loan.down_payment_pct * 100).toFixed(0)}
            onChange={(e) => setLoan({ down_payment_pct: +e.target.value / 100 })} />
        </LabeledField>
        <LabeledField label="Loan Term" hint="months">
          <Input type="number" min={12} max={120} step={12} value={loan.loan_term_months}
            onChange={(e) => setLoan({ loan_term_months: +e.target.value })} />
        </LabeledField>
      </div>

      <div className="border-t border-gray-100 mt-4 pt-4">
        <SectionTitle>Lease Parameters (Scenario 4)</SectionTitle>
      </div>

      <LabeledField label="Money Factor" hint="e.g. 0.00125">
        <Input type="number" min={0} step={0.00001} value={lease.money_factor}
          onChange={(e) => setLease({ money_factor: +e.target.value })} />
      </LabeledField>

      <div className="grid grid-cols-2 gap-3">
        <LabeledField label="Lease Term" hint="months">
          <Input type="number" min={12} max={72} step={12} value={lease.lease_term_months}
            onChange={(e) => setLease({ lease_term_months: +e.target.value })} />
        </LabeledField>
        <LabeledField label="Residual Value" hint="%">
          <Input type="number" min={0} max={100} step={1} value={(lease.residual_value_pct * 100).toFixed(0)}
            onChange={(e) => setLease({ residual_value_pct: +e.target.value / 100 })} />
        </LabeledField>
      </div>

      <div className="border-t border-gray-100 mt-4 pt-4">
        <SectionTitle>Analysis Settings</SectionTitle>
        <LabeledField label="Discount Rate" hint="%">
          <Input type="number" min={0} max={20} step={0.5} value={(discount_rate * 100).toFixed(1)}
            onChange={(e) => setDiscountRate(+e.target.value / 100)} />
        </LabeledField>
      </div>
    </div>
  );
}
