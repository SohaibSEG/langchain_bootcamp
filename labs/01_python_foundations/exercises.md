# Exercises: Python Foundations

Use these exercises to practice the notebook concepts. Write your own code and run it cell by cell.

## Exercise 1

Create variables for a new support ticket:

- ticket id
- customer name
- subject
- message
- channel

Print a one-line summary.

## Exercise 2

Represent the same ticket as a dictionary. Print only the subject and message.

## Exercise 3

Use required access to read the ticket subject with square brackets. Then use safe access with `.get()` to read a `priority` field that may not exist.

## Exercise 4

Create a new dictionary from the ticket using `**` destructuring/unpacking. Add `priority` and `queue` fields without changing the original ticket.

## Exercise 5

Convert your ticket dictionary to a JSON string with `json.dumps()`. Convert it back to a dictionary with `json.loads()`.

## Exercise 6

Create a list of three ticket dictionaries. Practice:

- first item access
- last item access
- slicing the first two items
- looping over every ticket id

## Exercise 7

Create a comma-separated string of labels such as `"billing,urgent,refund"`. Split it into a list, sort the list, and print the result.

## Exercise 8

Create a formatted ticket summary with an f-string. Include the ticket id, priority, and subject.

## Exercise 9

Write a function that accepts a ticket dictionary and returns `"urgent"` if the message contains words such as `"blocked"`, `"production"`, or `"charged twice"`.

## Exercise 10

Write a function with `ticket_id`, `subject`, and `priority` parameters. Call it once with positional arguments and once with named arguments.

## Exercise 11

Create a class named `SupportTicket` with attributes for id, subject, and message. Add a method that returns a short display title.

## Exercise 12

Create a subclass named `EscalatedTicket`. Override the display-title method so escalated tickets include the word `"URGENT"`.

## Exercise 13

Create an abstract class named `TicketFormatter` with an abstract method named `format`. Then create one concrete subclass that formats a ticket as a single-line summary.
