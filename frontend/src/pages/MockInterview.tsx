import { useState } from 'react';
import { Mic2, Sparkles, Loader2, CheckCircle2, XCircle, RotateCcw, RefreshCw, Send, Award, Mic, MicOff } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { api, ApiError } from '../lib/api';
import { SectionTitle, Badge } from '../components/Primitives';
import type { InterviewStartResponse, InterviewSubmitResponse } from '../types/api';

export function MockInterview() {
  const { candidateId, candidate } = useCandidate();
  const [session, setSession] = useState<InterviewStartResponse | null>(null);
  const [variant, setVariant] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InterviewSubmitResponse | null>(null);
  const [listeningId, setListeningId] = useState<string | null>(null);

  function toggleSpeech(questionId: string) {
    const win = window as unknown as {
      SpeechRecognition?: new () => any;
      webkitSpeechRecognition?: new () => any;
    };
    const SpeechRec = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SpeechRec) {
      alert('Speech recognition is not supported in this browser. Please type your response.');
      return;
    }
    if (listeningId === questionId) {
      setListeningId(null);
      return;
    }
    try {
      const recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      setListeningId(questionId);
      recognition.onresult = (event: any) => {
        const transcript = event.results?.[0]?.[0]?.transcript;
        if (transcript) {
          setAnswers((prev) => ({
            ...prev,
            [questionId]: prev[questionId] ? `${prev[questionId]} ${transcript}` : transcript,
          }));
        }
        setListeningId(null);
      };
      recognition.onerror = () => setListeningId(null);
      recognition.onend = () => setListeningId(null);
      recognition.start();
    } catch {
      setListeningId(null);
    }
  }

  async function start(v: number = variant) {
    setLoading(true);
    setError(null);
    setResult(null);
    setAnswers({});
    try {
      const res = await api.startInterview(candidateId, v);
      setSession(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not start interview.');
    } finally {
      setLoading(false);
    }
  }

  function handleDifferentQuestions() {
    const nextV = variant + 1;
    setVariant(nextV);
    start(nextV);
  }

  async function submit() {
    if (!session) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.submitInterview({
        candidate_id: candidateId,
        session_id: session.session_id,
        answers: session.questions.map((q) => ({
          question_id: q.question_id,
          answer_text: answers[q.question_id] || '',
        })),
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Scoring failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fade-up space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<Mic2 size={20} />}
          title="Technical Mock Interview"
          subtitle={`Interactive technical interview for ${candidate.name} targeting prerequisite weaknesses and verified depth`}
        />
        {session && !result && (
          <button
            onClick={handleDifferentQuestions}
            disabled={loading}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent border border-accent/30 transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Different Questions (Set #{variant + 1})
          </button>
        )}
      </div>

      {/* Intro card if not started */}
      {!session && !result && (
        <div className="card p-8 flex flex-col items-center text-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-accent/15 flex items-center justify-center text-accent">
            <Mic2 size={26} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Start Technical Mock Interview</h3>
            <p className="text-sm text-white/50 max-w-lg mt-1 leading-relaxed">
              Answer targeted questions evaluated by our deterministic scoring engine against explicit technical rubrics.
              Submitting thorough answers immediately updates your Career Twin and boosts your overall readiness score.
            </p>
          </div>
          <button
            onClick={() => start(0)}
            disabled={loading}
            className="flex items-center gap-2 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-sm px-6 py-2.5 rounded-xl transition-colors shadow-glow"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Generate Interview Questions
          </button>
        </div>
      )}

      {error && <p className="text-xs text-danger">{error}</p>}

      {/* Active Interview Form */}
      {session && !result && (
        <div className="space-y-5 fade-up">
          <div className="card p-4 flex items-center justify-between bg-white/[0.02]">
            <span className="text-xs text-white/60">
              Active Session: <strong className="text-white">{session.questions.length} Questions</strong> (Question Set #{variant + 1})
            </span>
            <span className="text-xs text-accent font-medium">Deterministic Rubric Evaluation Enabled</span>
          </div>

          {session.questions.map((q, idx) => {
            const currentAnswer = answers[q.question_id] || '';
            const words = currentAnswer.trim() ? currentAnswer.trim().split(/\s+/).length : 0;
            return (
              <div key={q.question_id} className="card p-6 space-y-4 border-white/5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-accent/20 text-accent text-xs font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <Badge className="bg-accent2/15 text-accent2 border-accent2/30 font-medium">{q.skill}</Badge>
                  </div>
                  <span className="text-xs text-white/40">{words} words written</span>
                </div>

                <p className="text-base font-semibold text-white leading-relaxed">{q.question}</p>

                {/* Rubric preview */}
                <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <p className="text-[11px] uppercase tracking-wider text-white/40 font-semibold mb-1.5">Evaluation Rubric Targets:</p>
                  <ul className="grid sm:grid-cols-2 gap-1.5">
                    {q.rubric.map((r, i) => (
                      <li key={i} className="text-xs text-white/60 flex items-start gap-1.5">
                        <span className="text-accent2 mt-0.5">•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <label className="text-xs text-white/50 font-medium">Your Technical Response:</label>
                  <button
                    type="button"
                    onClick={() => toggleSpeech(q.question_id)}
                    className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg border transition-all ${
                      listeningId === q.question_id
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                        : 'bg-white/5 text-white/70 border-white/10 hover:text-white hover:bg-white/10'
                    }`}
                    title="Speak your answer (Speech-to-Text)"
                  >
                    {listeningId === q.question_id ? (
                      <>
                        <MicOff size={13} className="text-rose-400" />
                        Listening… (Click to stop)
                      </>
                    ) : (
                      <>
                        <Mic size={13} className="text-accent" />
                        Dictate Answer
                      </>
                    )}
                  </button>
                </div>

                <textarea
                  value={currentAnswer}
                  onChange={(e) => setAnswers({ ...answers, [q.question_id]: e.target.value })}
                  rows={5}
                  placeholder={`Provide a thorough technical answer for ${q.skill}. Explain commands, architectural concepts, trade-offs, and failure recovery to maximize your score...`}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent/50 font-sans leading-relaxed"
                />
              </div>
            );
          })}

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={submit}
              disabled={submitting}
              className="flex items-center gap-2 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-sm px-6 py-2.5 rounded-xl transition-colors shadow-glow"
            >
              {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              Submit Answers for Evaluation
            </button>
          </div>
        </div>
      )}

      {/* Thorough Evaluation Results */}
      {result && (
        <div className="space-y-6 fade-up">
          <div className="card p-6 bg-gradient-to-br from-accent/10 to-accent2/10 border-accent/30 flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-2 text-accent2 mb-1">
                <Award size={18} />
                <span className="text-xs uppercase tracking-wider font-semibold">Evaluation Complete</span>
              </div>
              <h3 className="text-2xl font-bold text-white">
                Overall Interview Score: <span className="text-accent">{result.overall_score}/100</span>
              </h3>
              <p className="text-xs text-white/60 mt-1">
                {result.recorded_to_career_twin ? '✓ Answers analyzed in depth and permanently updated in Career Twin.' : 'Evaluated against deterministic rubric criteria.'}
              </p>
            </div>
            <button
              onClick={() => {
                setResult(null);
                start(variant + 1);
              }}
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white font-medium text-xs px-4 py-2 rounded-lg transition-colors"
            >
              <RotateCcw size={14} /> Try Another Question Set
            </button>
          </div>

          <div className="space-y-4">
            {result.per_question.map((q, idx) => (
              <div key={idx} className="card p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-white/10 text-xs font-bold flex items-center justify-center text-white/70">
                      {idx + 1}
                    </span>
                    <Badge className="bg-white/5 text-white/80 border-white/10">{q.skill}</Badge>
                  </div>
                  <span className={`text-base font-bold ${q.score >= 75 ? 'text-accent2' : q.score >= 50 ? 'text-warn' : 'text-danger'}`}>
                    {q.score} / 100
                  </span>
                </div>

                <p className="text-xs text-white/80 leading-relaxed font-medium bg-white/[0.02] p-3 rounded-lg border border-white/5">
                  {q.feedback}
                </p>

                <div className="grid sm:grid-cols-2 gap-3 pt-1">
                  {/* Hits */}
                  <div className="bg-accent2/[0.04] border border-accent2/20 rounded-xl p-3">
                    <p className="text-[11px] font-semibold text-accent2 flex items-center gap-1.5 mb-2">
                      <CheckCircle2 size={14} /> Rubric Concepts Satisfied ({q.rubric_hits.length})
                    </p>
                    {q.rubric_hits.length > 0 ? (
                      <ul className="space-y-1">
                        {q.rubric_hits.map((h, i) => (
                          <li key={i} className="text-xs text-white/70 flex items-start gap-1.5">
                            <span className="text-accent2">✓</span>
                            <span>{h}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-white/40 italic">No primary rubric criteria matched.</p>
                    )}
                  </div>

                  {/* Misses */}
                  <div className="bg-danger/[0.04] border border-danger/20 rounded-xl p-3">
                    <p className="text-[11px] font-semibold text-danger flex items-center gap-1.5 mb-2">
                      <XCircle size={14} /> Missing Criteria to Elaborate ({q.rubric_misses.length})
                    </p>
                    {q.rubric_misses.length > 0 ? (
                      <ul className="space-y-1">
                        {q.rubric_misses.map((m, i) => (
                          <li key={i} className="text-xs text-white/70 flex items-start gap-1.5">
                            <span className="text-danger">✗</span>
                            <span>{m}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-accent2 italic">All criteria met!</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
