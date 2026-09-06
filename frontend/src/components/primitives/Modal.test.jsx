import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Modal } from "./Modal";

describe("Modal", () => {
  it("is not rendered when closed", () => {
    render(
      <Modal title="Test" isOpen={false} onClose={() => {}}>
        content
      </Modal>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("exposes dialog semantics and closes on Escape (keyboard operability, §5.5)", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal title="Release to recipients" isOpen onClose={onClose}>
        content
      </Modal>,
    );

    const dialog = screen.getByRole("dialog", { name: "Release to recipients" });
    expect(dialog).toHaveAttribute("aria-modal", "true");

    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledOnce();
  });
});
