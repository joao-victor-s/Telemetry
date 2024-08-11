import { useRef } from "react";

/**
 * Same as React.useRef but uses lazy initializer function for expensive initial values.
 * @see {@link https://reactjs.org/docs/hooks-reference.html#useref}
 * @see {@link https://reactjs.org/docs/hooks-faq.html#how-to-create-expensive-objects-lazily}
 *
 * @param initializer A function that returns the first ref value.
 * @returns Current ref value
 */
export default function useLazyRef<T>(initializer: () => T): T {
  const ref = useRef<T | null>(null);
  if (ref.current === null) {
    ref.current = initializer();
  }

  return ref.current;
}
