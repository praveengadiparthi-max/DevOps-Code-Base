import { useEffect, useRef, useState } from 'react'
import { tailorFromUpload, tailorFromText } from './api/resumeApi'
import DownloadSection from './components/DownloadSection'
import JobDescriptionInput from './components/JobDescriptionInput'
import ResumeInput from './components/ResumeInput'
import StatusMessage from './components/StatusMessage'
import TailorButton from './components/TailorButton'

const INITIAL_STATE = {
  phase: 'idle',       // 'idle' | 'processing' | 'ready' | 'error'
  inputMode: 'upload', // 'upload' | 'paste'
  file: null,
  resumeText: '',
  jobDescription: '',
  downloadToken: null,
  errorMessage: null,
  progress: 0,
}

export default function App() {
  const [state, setState] = useState(INITIAL_STATE)
  const progressTimer = useRef(null)

  function patch(updates) {
    setState((s) => ({ ...s, ...updates }))
  }

  function handleResumeChange({ mode, file, text }) {
    patch({ inputMode: mode, file: file ?? state.file, resumeText: text ?? state.resumeText })
  }

  function isReady() {
    const hasResume =
      state.inputMode === 'upload' ? !!state.file : state.resumeText.trim().length >= 50
    return hasResume && state.jobDescription.trim().length >= 20
  }

  function startFakeProgress() {
    patch({ progress: 5 })
    let current = 5
    progressTimer.current = setInterval(() => {
      current = current < 85 ? current + Math.random() * 4 : current
      patch({ progress: Math.min(Math.round(current), 85) })
    }, 800)
  }

  function stopFakeProgress() {
    clearInterval(progressTimer.current)
  }

  async function handleTailor() {
    patch({ phase: 'processing', errorMessage: null, progress: 0 })
    startFakeProgress()
    try {
      let data
      if (state.inputMode === 'upload') {
        data = await tailorFromUpload(state.file, state.jobDescription, (pct) =>
          patch({ progress: pct }),
        )
      } else {
        data = await tailorFromText(state.resumeText, state.jobDescription)
      }
      stopFakeProgress()
      patch({ progress: 100, phase: 'ready', downloadToken: data.download_token })
    } catch (err) {
      stopFakeProgress()
      patch({ phase: 'error', errorMessage: err.message, progress: 0 })
    }
  }

  function handleReset() {
    stopFakeProgress()
    setState(INITIAL_STATE)
  }

  useEffect(() => () => clearInterval(progressTimer.current), [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-brand shadow-md py-5 px-6">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-3xl">📝</span>
          <div>
            <h1 className="text-white text-xl font-bold leading-tight">Resume Tailor</h1>
            <p className="text-blue-200 text-xs">AI-powered resume customization</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10">
        {/* Intro */}
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Tailor your resume to any job in seconds
          </h2>
          <p className="text-gray-500 text-base max-w-xl mx-auto">
            Upload your resume and paste a job description. Claude AI will rewrite your resume to
            highlight the skills and experience that matter most for that specific role.
          </p>
        </div>

        {state.phase === 'ready' ? (
          <DownloadSection token={state.downloadToken} onReset={handleReset} />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left column */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <ResumeInput
                onChange={handleResumeChange}
                disabled={state.phase === 'processing'}
              />
            </div>

            {/* Right column */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <JobDescriptionInput
                value={state.jobDescription}
                onChange={(val) => patch({ jobDescription: val })}
                disabled={state.phase === 'processing'}
              />
            </div>

            {/* Full-width bottom */}
            <div className="lg:col-span-2 space-y-4">
              {state.phase === 'processing' && (
                <StatusMessage progress={state.progress} />
              )}

              {state.phase === 'error' && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                  <strong>Error:</strong> {state.errorMessage}
                </div>
              )}

              <TailorButton
                onClick={handleTailor}
                disabled={!isReady()}
                loading={state.phase === 'processing'}
              />

              <p className="text-center text-xs text-gray-400">
                Your resume is processed securely and never stored permanently.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
