import { Pill, X } from "lucide-react";

interface MedicationTagProps {
  name: string;
  dosage?: string;
  onRemove?: () => void;
}

export function MedicationTag({ name, dosage, onRemove }: MedicationTagProps) {
  return (
    <div className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#009688]/10 border-2 border-[#009688] rounded-lg">
      <Pill className="w-4 h-4 text-[#009688]" />
      <div className="flex flex-col">
        <span className="text-sm font-medium text-[#263238]">{name}</span>
        {dosage && <span className="text-xs text-gray-600">{dosage}</span>}
      </div>
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-2 hover:opacity-70 text-[#009688]"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
