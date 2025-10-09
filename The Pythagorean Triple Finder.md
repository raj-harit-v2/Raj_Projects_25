Here is a template for the project prompt, focusing on the multi-step requirements of **The Pythagorean Triple Finder and Analyzer**.

---

## Project Prompt Template: The Pythagorean Triple Finder and Analyzer 📐

### Project Goal

Develop a program that systematically **generates**, **analyzes**, and **verifies** Pythagorean Triples. The program must demonstrate proficiency in iterative logic, number theory, and structured data handling.

### Core Requirements (Must-Have Features)

Your program must implement a robust menu system that allows the user to choose between the following two primary functions:

#### 1. Generate and Analyze Triples

This function must generate all **primitive** and **non-primitive** Pythagorean Triples $(a, b, c)$ up to a user-defined maximum value for the hypotenuse, $c$.

* **Input:** The user specifies an integer for the **Maximum Hypotenuse ($c_{max}$)** (e.g., 50).
* **Multi-Step Process:**
    * Use an iterative method (like **nested loops** based on Euclid's formula or a variation) to search for triples where $c \le c_{max}$.
    * For every triple found, calculate the **Greatest Common Divisor (GCD)** of $a$ and $b$ to determine if the triple is **primitive** ($\text{GCD}(a, b) = 1$) or **non-primitive** ($\text{GCD}(a, b) > 1$).
    * Store all found triples.
* **Output:** Print the results in a formatted list, clearly grouping or labeling the triples as **Primitive** or **Non-Primitive**.

#### 2. Verify and Analyze a Custom Triple

This function must check a set of three user-provided integers.

* **Input:** The user provides three positive integers ($x, y, z$).
* **Multi-Step Process:**
    * **Verification:** Determine if the three numbers form a Pythagorean Triple (i.e., check if $x^2 + y^2 = z^2$ or a permutation thereof, assuming $z$ is the largest side).
    * **Error/Logic Check:** If they *do not* form a triple, state this clearly and stop the analysis.
    * **Primitivity Analysis:** If they *do* form a triple, use the GCD method to classify them as **Primitive** or **Non-Primitive**.
* **Output:** A clear statement on whether the input is a Pythagorean Triple, and if so, whether it is Primitive or Non-Primitive.

---

### Constraints and Testing Rules

1.  **Complexity Rule:** The project **must not be a simple mathematical problem**. It must involve multiple logical and computational steps (e.g., iteration, data storage, conditional logic, and GCD calculation).
2.  **Input/Output:** All inputs must be handled robustly (e.g., ensure the user enters positive integers). All output must be clearly labeled and readable.
3.  **Required Test Cases:** Your final submission must include passing tests for:
    * **Generation Test:** Generating triples up to $c_{max}=25$. The output must correctly include the primitive triple **(5, 12, 13)** and the non-primitive triple **(6, 8, 10)**.
    * **Verification Test 1 (Success):** Inputting **(8, 15, 17)** and correctly identifying it as a **Primitive** Triple.
    * **Verification Test 2 (Failure):** Inputting **(2, 3, 4)** and stating clearly that it **is not a Pythagorean Triple**.

---