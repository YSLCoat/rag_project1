import { useState, FormEvent } from 'react'
import './App.css'

// Eksisterende interface
interface ClaimVerificationResult {
  claim: string;
  verification: string;
}

// NY interface for URL-resultatet
interface UrlVerificationResult {
  url: string;
  verification: string;
}

function App() {
  const [claimInput, setClaimInput] = useState<string>('');
  const [result, setResult] = useState<ClaimVerificationResult | null>(null);
  const [urlInput, setUrlInput] = useState<string>('');
  const [urlResult, setUrlResult] = useState<UrlVerificationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const claimApiUrl = `${import.meta.env.VITE_API_BASE_URL}/validate_claim`;
  const urlApiUrl = `${import.meta.env.VITE_API_BASE_URL}/validate_news_article_content`;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault(); 
    
    if (!claimInput.trim()) {
      setError('Vennligst skriv inn en påstand som skal verifiseres.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setUrlResult(null);

    try {
      const response = await fetch(claimApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: claimInput }), 
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data: ClaimVerificationResult = await response.json();
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

  const handleUrlSubmit = async (event: FormEvent) => {
    event.preventDefault(); 
    
    if (!urlInput.trim()) {
      setError('Vennligst skriv inn en URL som skal analyseres.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setUrlResult(null);

    try {
      const response = await fetch(urlApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: urlInput }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data: UrlVerificationResult = await response.json();
      setUrlResult(data);

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
        <h1>Heimdall</h1>
        <p className="p1">Verifiser påstander og analyser artikler</p>
      </header>
      
      <main>
        <p className="p2">Skriv en påstand knyttet til et partis politikk og trykk 'verifiser'.</p>
        <form onSubmit={handleSubmit} className="claim-form">
          <textarea
            value={claimInput}
            onChange={(e) => setClaimInput(e.target.value)}
            placeholder="Eks: 'Partiet Rødt vil øke skattene for alle'"
            rows={4}
            disabled={isLoading}
            aria-label="Political claim input"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Verifiserer...' : 'Verifiser påstand'}
          </button>
        </form>

        <p className="p2" style={{marginTop: '2.5rem', marginBottom: '1.2rem'}}>
          Eller, lim inn en URL til en nyhetsartikkel for full analyse:
        </p>
        <form onSubmit={handleUrlSubmit} className="claim-form">
          <input
            type="url"
            className="url-input" // Egen klasse for styling
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Eks: https://www.nrk.no/..."
            disabled={isLoading}
            aria-label="News article URL input"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Analyserer...' : 'Analyser URL'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {result && (
          <div className="result-card">
            <h2>Verifisering av påstand</h2>
            <div className="result-item">
              <h3>Opprinnelig påstand</h3>
              <p>{result.claim}</p>
            </div>
            <div className="result-item">
              <h3>Verifisering</h3>
              <p>{result.verification}</p>
            </div>
          </div>
        )}

        {urlResult && (
          <div className="result-card">
            <h2>Analyse av artikkel</h2>
            <div className="result-item">
              <h3>Kilde-URL</h3>
              <p>
                <a href={urlResult.url} target="_blank" rel="noopener noreferrer">
                  {urlResult.url}
                </a>
              </p>
            </div>
            <div className="result-item">
              <h3>Analyse</h3>
              <p>{urlResult.verification}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App