import { ChangeEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const UploadForm = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [analysisType, setAnalysisType] = useState("plagiarism");

  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const getAIColor = (score: number) => {
    if (score > 0.7) return "#ff4d4f";
    if (score > 0.4) return "#faad14";
    return "#52c41a";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) return;

    if (!token) {
      setError("You are not logged in.");
      navigate("/login");
      return;
    }

    setIsUploading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append("analysis_type", analysisType);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/documents/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (response.status === 401) {
        logout();
        navigate("/login");
        return;
      }

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText);
      }

      const data = await response.json();

      setResults(data?.data); // 🔥 IMPORTANT
      setFiles([]);
    } catch (e: any) {
      setError(e.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  function handleFileChange(event: ChangeEvent<HTMLInputElement>): void {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      setFiles(Array.from(selectedFiles));
    }
  }

  return (
    <div className="container fade-in" style={{ padding: "60px 0" }}>
      <div style={{ marginBottom: "60px", textAlign: "center" }}>
        <h1 className="text-gradient" style={{ fontSize: "56px", fontWeight: 800 }}>
          Analyze Content
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "18px" }}>
          Upload documents for deep AI & plagiarism analysis.
        </p>
      </div>

      <div className="glass" style={{ padding: "48px", borderRadius: "32px" }}>
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "40px" }}
        >
          {/* Analysis Type */}
          <div>
            <label style={{ fontWeight: 700 }}>Analysis Mode</label>

            <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
              {["plagiarism", "ai", "both"].map((type) => (
                <label key={type}>
                  <input
                    type="radio"
                    value={type}
                    checked={analysisType === type}
                    onChange={(e) => setAnalysisType(e.target.value)}
                  />
                  {" "}
                  {type.toUpperCase()}
                </label>
              ))}
            </div>
          </div>

          <input type="file" multiple onChange={handleFileChange} />

          <button
            type="submit"
            disabled={files.length === 0 || isUploading}
            className="btn-primary"
          >
            {isUploading ? "Processing..." : "Start Analysis"}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: "30px", color: "#ff4d4f" }}>
            ⚠️ {error}
          </div>
        )}

        {/* ================= RESULTS SECTION ================= */}
        {results && (
          <div style={{ marginTop: "50px" }}>
            <h2 style={{ marginBottom: "25px" }}>📊 Analysis Results</h2>

            {/* DOCUMENT RESULTS */}
            {results.documents?.map((doc: any, index: number) => (
              <div
                key={index}
                style={{
                  background: "#1f1f1f",
                  padding: "25px",
                  borderRadius: "18px",
                  marginBottom: "25px",
                  border: "1px solid #2c2c2c",
                }}
              >
                <h3>{doc.filename}</h3>

                {analysisType !== "plagiarism" && (
                  <>
                    <div
                      style={{
                        marginTop: "10px",
                        padding: "8px 14px",
                        borderRadius: "8px",
                        background: getAIColor(doc.ai_score),
                        color: "white",
                        fontWeight: 600,
                        display: "inline-block",
                      }}
                    >
                      {doc.is_ai_generated
                        ? "🤖 AI Generated"
                        : "🧑 Human Written"}
                    </div>

                    <p style={{ marginTop: "12px" }}>
                      AI Score: {(doc.ai_score * 100).toFixed(2)}%
                    </p>
                  </>
                )}
              </div>
            ))}

            {/* PLAGIARISM RESULTS */}
            {results.plagiarism?.length > 0 && (
              <div style={{ marginTop: "40px" }}>
                <h3 style={{ marginBottom: "15px" }}>
                  🔍 Plagiarism Similarity
                </h3>

                {results.plagiarism.map((p: any, index: number) => (
                  <div key={index} style={{ marginBottom: "20px" }}>
                    <div
                      style={{
                        height: "22px",
                        background: "#2a2a2a",
                        borderRadius: "12px",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${Number(p.similarity_score) || 0}%`,
                          height: "100%",
                          transition: "width 0.6s ease-in-out",
                          background:
                            p.similarity_score > 70
                              ? "#ff4d4f"
                              : p.similarity_score > 40
                              ? "#faad14"
                              : "#52c41a",
                        }}
                      />
                    </div>

                    <p style={{ marginTop: "8px" }}>
                      Similarity:{" "}
                      {Number(p.similarity_score || 0).toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;
