import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Register from "@/pages/Register"; // Adjust path as needed

// ---- Mocks ----

// Mock auth module
vi.mock("@/api/auth", () => ({
  registerUser: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock alert
const mockAlert = vi.fn();
global.alert = mockAlert as any;

// Mock HeroUI components - Fixed to properly handle form submission
vi.mock("@heroui/react", () => ({
  Button: ({ children, onPress, isLoading, type, ...props }: any) => (
    <button 
      onClick={onPress} 
      disabled={isLoading} 
      type={type}
      data-testid="submit-button"
      {...props}
    >
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
    onKeyDown, // Add onKeyDown handler
    ...props
  }: any) => (
    <div>
      {label && <label data-testid={`label-${label.toLowerCase().replace(/\s+/g, '-')}`}>{label}</label>}
      <input
        data-testid={`input-${label?.toLowerCase().replace(/\s+/g, '-') || "input"}`}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onValueChange && onValueChange(e.target.value)}
        onKeyDown={onKeyDown} // Pass onKeyDown
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

// Import the mocked function
import { registerUser } from "@/api/auth";
const mockedRegisterUser = vi.mocked(registerUser);

// ---- Tests ----

describe("Register Page", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockedRegisterUser.mockReset();
    mockNavigate.mockReset();
    mockAlert.mockReset();
  });

  it("renders registration form with all elements", () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Check headings
    expect(screen.getByText("Create Account")).toBeInTheDocument();
    expect(screen.getByText(/Join the Chemical PFD Builder team/i)).toBeInTheDocument();

    // Check all form inputs
    expect(screen.getByTestId("input-username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Choose a username/i)).toBeInTheDocument();

    expect(screen.getByTestId("input-email")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your email/i)).toBeInTheDocument();

    expect(screen.getByTestId("input-password")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Create a password/i)).toBeInTheDocument();

    expect(screen.getByTestId("input-confirm-password")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Confirm your password/i)).toBeInTheDocument();

    // Check button
    expect(screen.getByText("Sign Up")).toBeInTheDocument();

    // Check login link
    expect(screen.getByText(/Already have an account?/i)).toBeInTheDocument();
    const loginLink = screen.getByText("Log In");
    expect(loginLink).toBeInTheDocument();
    expect(loginLink.closest("a")).toHaveAttribute("href", "/login");
  });

  it("updates form fields when user types", () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const usernameInput = screen.getByTestId("input-username");
    const emailInput = screen.getByTestId("input-email");
    const passwordInput = screen.getByTestId("input-password");
    const confirmPasswordInput = screen.getByTestId("input-confirm-password");

    // Type in inputs
    fireEvent.change(usernameInput, { target: { value: "testuser" } });
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "password123" } });

    expect(usernameInput).toHaveValue("testuser");
    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
    expect(confirmPasswordInput).toHaveValue("password123");
  });

  it("validates password match before submission", async () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form with mismatched passwords
    fireEvent.change(screen.getByTestId("input-username"), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByTestId("input-email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByTestId("input-password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByTestId("input-confirm-password"), {
      target: { value: "differentpassword" },
    });

    // Submit form
    fireEvent.click(screen.getByTestId("submit-button"));

    // Should show alert and not call registerUser
    expect(mockAlert).toHaveBeenCalledWith("Passwords do not match!");
    expect(mockedRegisterUser).not.toHaveBeenCalled();
  });

  it("calls registerUser with correct data on form submit", async () => {
    mockedRegisterUser.mockResolvedValue({} as any);

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form with matching passwords
    fireEvent.change(screen.getByTestId("input-username"), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByTestId("input-email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByTestId("input-password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByTestId("input-confirm-password"), {
      target: { value: "password123" },
    });

    // Submit form
    await act(async () => {
      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Wait for async operation
    await waitFor(() => {
      expect(mockedRegisterUser).toHaveBeenCalledWith(
        "testuser",
        "test@example.com",
        "password123"
      );
    });
  });

  it("shows success alert and navigates to login on successful registration", async () => {
    mockedRegisterUser.mockResolvedValue({} as any);

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill and submit form
    await act(async () => {
      fireEvent.change(screen.getByTestId("input-username"), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByTestId("input-email"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByTestId("input-password"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByTestId("input-confirm-password"), {
        target: { value: "password123" },
      });

      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Wait for async operations
    await waitFor(() => {
      expect(mockAlert).toHaveBeenCalledWith(
        "Registration successful! Please login."
      );
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });

  it("shows alert on registration failure", async () => {
    mockedRegisterUser.mockRejectedValue(new Error("Registration failed"));

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill and submit form
    await act(async () => {
      fireEvent.change(screen.getByTestId("input-username"), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByTestId("input-email"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByTestId("input-password"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByTestId("input-confirm-password"), {
        target: { value: "password123" },
      });

      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Wait for async operation
    await waitFor(() => {
      expect(mockAlert).toHaveBeenCalledWith(
        "Registration failed. Please try again."
      );
    });

    // Should not navigate on failure
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("shows loading state during registration", async () => {
    // Create a promise that we can resolve manually
    let resolveRegister: (value: any) => void;
    const registerPromise = new Promise((resolve) => {
      resolveRegister = resolve;
    });
    mockedRegisterUser.mockReturnValue(registerPromise as any);

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form
    await act(async () => {
      fireEvent.change(screen.getByTestId("input-username"), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByTestId("input-email"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByTestId("input-password"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByTestId("input-confirm-password"), {
        target: { value: "password123" },
      });

      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Check loading state
    await waitFor(() => {
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    // Resolve the promise
    await act(async () => {
      resolveRegister!({});
    });

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
    });
  });

  it("prevents form submission when passwords don't match", async () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form with mismatched passwords
    await act(async () => {
      fireEvent.change(screen.getByTestId("input-username"), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByTestId("input-email"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByTestId("input-password"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByTestId("input-confirm-password"), {
        target: { value: "different" },
      });

      // Submit form
      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Should not call API
    expect(mockedRegisterUser).not.toHaveBeenCalled();
    // Should show alert
    expect(mockAlert).toHaveBeenCalledWith("Passwords do not match!");
  });

  it("handles form submission via Enter key", async () => {
    mockedRegisterUser.mockResolvedValue({} as any);

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form
    const usernameInput = screen.getByTestId("input-username");
    const emailInput = screen.getByTestId("input-email");
    const passwordInput = screen.getByTestId("input-password");
    const confirmPasswordInput = screen.getByTestId("input-confirm-password");

    await act(async () => {
      fireEvent.change(usernameInput, { target: { value: "testuser" } });
      fireEvent.change(emailInput, { target: { value: "test@example.com" } });
      fireEvent.change(passwordInput, { target: { value: "password123" } });
      fireEvent.change(confirmPasswordInput, { target: { value: "password123" } });

      // Submit form by pressing Enter in the last input
      // First, we need to submit the form itself
      const form = screen.getByRole('form') || confirmPasswordInput.closest('form');
      
      if (form) {
        // Simulate form submission via Enter key
        fireEvent.submit(form);
      } else {
        // Fallback: fire Enter key on the input and check for form submission
        fireEvent.keyDown(confirmPasswordInput, { key: "Enter", code: "Enter", keyCode: 13 });
      }
    });

    await waitFor(() => {
      expect(mockedRegisterUser).toHaveBeenCalled();
    });
  });

  it("disables submit button when loading", async () => {
    let resolveRegister: (value: any) => void;
    const registerPromise = new Promise((resolve) => {
      resolveRegister = resolve;
    });
    mockedRegisterUser.mockReturnValue(registerPromise as any);

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    // Fill form
    await act(async () => {
      fireEvent.change(screen.getByTestId("input-username"), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByTestId("input-email"), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByTestId("input-password"), {
        target: { value: "password123" },
      });
      fireEvent.change(screen.getByTestId("input-confirm-password"), {
        target: { value: "password123" },
      });

      // Submit form
      fireEvent.click(screen.getByTestId("submit-button"));
    });

    // Button should be disabled during loading
    await waitFor(() => {
      const button = screen.getByTestId("submit-button");
      expect(button).toBeDisabled();
      expect(button).toHaveTextContent("Loading...");
    });

    // Clean up
    await act(async () => {
      resolveRegister!({});
    });
  });
});