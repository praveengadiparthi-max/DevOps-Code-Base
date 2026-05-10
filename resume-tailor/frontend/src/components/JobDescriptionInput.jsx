export default function JobDescriptionInput({ value, onChange, disabled }) {
  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Job Description
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Paste the full job posting here — the more detail, the better the tailoring…"
        maxLength={20000}
        rows={12}
        className="w-full border border-gray-300 rounded-xl p-4 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand resize-y disabled:opacity-50"
      />
      <p className="text-xs text-gray-400 text-right mt-1">{value.length.toLocaleString()} / 20,000</p>
    </div>
  )
}
