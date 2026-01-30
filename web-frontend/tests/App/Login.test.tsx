import React, { act } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "@/pages/Login";

 
// ---- Mocks ----

// 1) Mock the auth module by providing a loginUser mock *inside* the factory (safe from hoisting).
vi.mock("@/api/auth", () => ({
  // Define a mock function here; we will import it below and use `vi.mocked` to control behavior
  loginUser: vi.fn(),
}));

// 2) Mock react-router-dom's useNavigate to return a stable mock function.
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  // importActual ensures we keep other react-router-dom exports intact
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// 3) Mock alert globally (simple spy)
const mockAlert = vi.fn();
// assign to global so code calling `alert()` will hit this mock
global.alert = mockAlert as any;

// 4) Mock HeroUI components (only what Login uses). Put simple accessible implementations here.
vi.mock("@heroui/react", () => ({
  Button: ({ children, onPress, isLoading, ...props }: any) => (
    <button onClick={onPress} disabled={isLoading} data-testid="button" {...props}>
      {isLoading ? "Loading..." : children}
    </button>
  ),
  Input: ({
    label,
    placeholder,
    type = "text",
    value,
    onValueChange,
    variant,
    isRequired,
    ...props
  }: any) => (
    <div>
      {label && <label>{label}</label>}
      <input
        data-testid={`input-${label?.toLowerCase() || "input"}`}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onValueChange && onValueChange(e.target.value)}
        required={isRequired}
        {...props}
      />
    </div>
  ),
  Card: ({ children, className, ...props }: any) => (
    <div className={className} data-testid="card" {...props}>
      {children}
    </div>
  ),
  CardHeader: ({ children, className, ...props }: any) => (
    <div className={className} data-testid="card-header" {...props}>
      {children}
    </div>
  ),
  CardBody: ({ children, className, ...props }: any) => (
    <div className={className} data-testid="card-body" {...props}>
      {children}
    </div>
  ),
  Divider: ({ className, ...props }: any) => (
    <hr className={className} data-testid="divider" {...props} />
  ),
}));

// ---- Helper: get the mocked loginUser to control it in tests ----
import { loginUser } from "@/api/auth";
const mockedLoginUser = vi.mocked(loginUser);

// ---- Tests ----

describe("Login Page", () => {
  beforeEach(() => {
    // Reset all mocks between tests for isolation
    vi.resetAllMocks();
    mockedLoginUser.mockReset();
    mockNavigate.mockReset();
    mockAlert.mockReset();
  });

  it("renders login form with all elements", () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    // Check headings
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
    expect(screen.getByText(/Log in to access your diagrams/i)).toBeInTheDocument();

    // Check form inputs
    expect(screen.getByTestId("input-username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your username/i)).toBeInTheDocument();

    expect(screen.getByTestId("input-password")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your password/i)).toBeInTheDocument();

    // Check buttons and links
    expect(screen.getByText(/Forgot password/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign Up/i)).toBeInTheDocument();
  });

  it("updates form fields when user types", () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    const usernameInput = screen.getByPlaceholderText(/Enter your username/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);

    // Type in inputs
    fireEvent.change(usernameInput, { target: { value: "testuser" } });
    fireEvent.change(passwordInput, { target: { value: "testpass123" } });

    expect(usernameInput).toHaveValue("testuser");
    expect(passwordInput).toHaveValue("testpass123");
    
  });

  it("calls loginUser with correct credentials on form submit", async () => {
    // Arrange: make loginUser resolve successfully
    mockedLoginUser.mockResolvedValue({ token: "test-token" } as any);

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    // Fill form
    const usernameInput = screen.getByPlaceholderText(/Enter your username/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);
    const submitButton = screen.getByText(/Sign In/i);

    
    await act(async () => {
        fireEvent.change(usernameInput, { target: { value: "testuser" } });
        fireEvent.change(passwordInput, { target: { value: "testpass" } });
        fireEvent.click(submitButton);
    });
    // Check that loginUser was called with correct credentials
    expect(mockedLoginUser).toHaveBeenCalledWith("testuser", "testpass");
  });

  it("navigates to dashboard on successful login", async () => {
    mockedLoginUser.mockResolvedValue({ token: "test-token" } as any);

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    // Fill and submit form
    fireEvent.change(screen.getByPlaceholderText(/Enter your username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Enter your password/i), {
      target: { value: "testpass" },
    });
    fireEvent.click(screen.getByText(/Sign In/i));

    // Wait for async operation and assert navigation
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows alert on login failure", async () => {
    mockedLoginUser.mockRejectedValue(new Error("Invalid credentials"));

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    // Fill and submit form
    fireEvent.change(screen.getByPlaceholderText(/Enter your username/i), {
      target: { value: "wronguser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Enter your password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByText(/Sign In/i));

    // Wait for async operation
    await waitFor(() => {
      expect(mockAlert).toHaveBeenCalledWith(
        "Login failed! Please check your credentials.",
      );
    });
  });

  it("shows loading state during login", async () => {
    // Create a promise that we can resolve manually
    let resolveLogin: (value: any) => void;
    const loginPromise = new Promise((resolve) => {
      resolveLogin = resolve;
    });
    mockedLoginUser.mockReturnValue(loginPromise as any);

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    // Fill and submit form
    fireEvent.change(screen.getByPlaceholderText(/Enter your username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Enter your password/i), {
      target: { value: "testpass" },
    });
    fireEvent.click(screen.getByText(/Sign In/i));

    // Button should show loading state
    await waitFor(() => {
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    // Resolve the promise to finish the login flow
    resolveLogin!({ token: "test-token" });

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
    });
  });
});
