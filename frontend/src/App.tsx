import { useState, FormEvent } from 'react'
import './App.css'

interface VerificationResult {
  claim: string;
  verification: string;
}

function App() {
  const [claimInput, setClaimInput] = useState<string>('');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/validate_claim`;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault(); 
    
    if (!claimInput.trim()) {
      setError('Please enter a claim to verify.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: claimInput }), 
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data: VerificationResult = await response.json();
      setResult(data);

    } catch (err) {
      if (err instanceof Error) {
        setError(`Failed to get verification. Is the backend server running? (Details: ${err.message})`);
      } else {
        setError('An unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Political Claim Verifier</h1>
        <p>Enter a political claim below, and our AI-powered system will provide a verification.</p>
      </header>
      
      <main>
        <form onSubmit={handleSubmit} className="claim-form">
          <textarea
            value={claimInput}
            onChange={(e) => setClaimInput(e.target.value)}
            placeholder="e.g., 'The economy grew by 5% last quarter.'"
            rows={4}
            disabled={isLoading}
            aria-label="Political claim input"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Verifying...' : 'Verify Claim'}
          </button>
        </form>

        {/* Conditionally render error message */}
        {error && <div className="error-message">{error}</div>}

        {/* Conditionally render the result card */}
        {result && (
          <div className="result-card">
            <h2>Verification Result</h2>
            <div className="result-item">
              <h3>Original Claim</h3>
              <p>{result.claim}</p>
            </div>
            <div className="result-item">
              <h3>Verification</h3>
              <p>{result.verification}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App