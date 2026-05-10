export default function TailorButton({ onClick, disabled, loading }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`w-full py-4 rounded-xl text-white font-bold text-lg transition-all shadow-md ${
        disabled || loading
          ? 'bg-gray-300 cursor-not-allowed shadow-none'
          : 'bg-brand hover:bg-brand-light active:scale-[0.98] cursor-pointer'
      }`}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-3">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Tailoring…
        </span>
      ) : (
        '✨ Tailor My Resume'
      )}
    </button>
  )
}
