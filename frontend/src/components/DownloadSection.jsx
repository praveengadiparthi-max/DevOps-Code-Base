import { getDownloadUrl } from '../api/resumeApi'

export default function DownloadSection({ token, onReset }) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
      <div className="text-5xl mb-3">✅</div>
      <h2 className="text-xl font-bold text-green-800 mb-1">Your tailored resume is ready!</h2>
      <p className="text-green-600 text-sm mb-6">
        Customized to match the job description using Claude AI.
      </p>

      <a
        href={getDownloadUrl(token)}
        download="tailored_resume.pdf"
        className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold px-8 py-3 rounded-xl shadow transition-colors mb-4"
      >
        ⬇ Download PDF
      </a>

      <p className="text-xs text-gray-400 mb-6">Download link expires in 10 minutes · One-time use</p>

      <button
        onClick={onReset}
        className="text-sm text-gray-500 hover:text-brand underline transition-colors"
      >
        Tailor another resume
      </button>
    </div>
  )
}
