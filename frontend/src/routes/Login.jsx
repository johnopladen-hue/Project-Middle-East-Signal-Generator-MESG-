import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../app/AuthContext";
import { ApiError } from "../api/client";
import { Button } from "../components/primitives/Button";
import { FormField } from "../components/primitives/FormField";

export function Login() {
  const { user, login, isLoggingIn } = useAuth();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [retryAfterSeconds, setRetryAfterSeconds] = useState(null);

  if (user) {
    const from = location.state?.from?.pathname ?? "/";
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setRetryAfterSeconds(null);
    try {
      await login(username, password);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setRetryAfterSeconds(err.retryAfterSeconds);
      } else {
        // Generic on purpose — never reveal which field was wrong (§7).
        setError("Incorrect username or password.");
      }
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center p-8">
      <h1 className="mb-6 text-xl font-semibold text-ink">Sign in</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <FormField
          label="Username"
          name="username"
          autoComplete="username"
          value={username}
          disabled={isLoggingIn}
          onChange={(event) => setUsername(event.target.value)}
        />
        <FormField
          label="Password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          disabled={isLoggingIn}
          onChange={(event) => setPassword(event.target.value)}
        />

        {retryAfterSeconds != null ? (
          <p role="alert" className="text-sm text-grade-1">
            Too many attempts — try again in {retryAfterSeconds}s.
          </p>
        ) : error ? (
          <p role="alert" className="text-sm text-grade-1">
            {error}
          </p>
        ) : null}

        <Button type="submit" busy={isLoggingIn} disabled={retryAfterSeconds != null}>
          Sign in
        </Button>
      </form>
    </main>
  );
}
