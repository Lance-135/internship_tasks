import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

test("username boundary validation", () => {
  render(<App />);
  const input = screen.getByPlaceholderText("Enter username")
  const submit = screen.getByText("Submit")


  // TEST CASES

  // VALID TEST CASES 
  // "abc" -> min valid characters (3)
  fireEvent.change(input, { target: { value: "abc" } });
  fireEvent.click(submit)
  expect(screen.getByText(/no error/i));

  // "abcdefghijklmnopqrst" -> max valid characters (4)
  fireEvent.change(input, { target: { value: "abcdefghijklmnopqrst" } });
  fireEvent.click(submit)
  expect(screen.getByText(/no error/i));


  // "username_allowed"  -> allowed charactes
  fireEvent.change(input, { target: { value: "username_allowed" } });
  fireEvent.click(submit)
  expect(screen.getByText(/no error/i));



  // INVALID TEST CASES
  //"ab" -> below min valid characters(3)
  fireEvent.change(input, { target: { value: "ab" } });
  fireEvent.click(submit)
  expect(screen.getByText(/Error: Username must be at least 3 characters long/i));

  // "abcdefghijklmnopqrstu" -> above max valid characters (20)
  fireEvent.change(input, { target: { value: "abcdefghijklmnopqrstu" } });
  fireEvent.click(submit)
  expect(screen.getByText(/Error: Username must not exceed 20 characters./i));
  
  // "user!@#" -> invalid characters (fuzzy inputs)
  fireEvent.change(input, { target: { value: "user!@#" } });
  fireEvent.click(submit)
  expect(screen.getByText(/Username must be letters and numbers/i));
});


