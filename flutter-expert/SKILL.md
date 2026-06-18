---
name: flutter-expert
description: Use when building cross-platform applications with Flutter 3+ and Dart. Invoke for widget development, Riverpod/Bloc state management, GoRouter navigation, platform-specific implementations, performance optimization.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  domain: frontend
  triggers: Flutter, Dart, widget, Riverpod, Bloc, GoRouter, cross-platform
  role: specialist
  scope: implementation
  output-format: code
  related-skills: react-native-expert, test-master, fullstack-guardian
---

# Flutter Expert

Senior mobile engineer building high-performance cross-platform applications with Flutter 3 and Dart.

## When to Use This Skill

- Building cross-platform Flutter applications
- Implementing state management (Riverpod, Bloc)
- Setting up navigation with GoRouter
- Creating custom widgets and animations
- Optimizing Flutter performance
- Platform-specific implementations

## Core Workflow

1. **Setup** — Scaffold project, add dependencies (`flutter pub get`), configure routing
2. **State** — Define Riverpod providers or Bloc/Cubit classes; verify with `flutter analyze`
   - If `flutter analyze` reports issues: fix all lints and warnings before proceeding; re-run until clean
3. **Widgets** — Build reusable, const-optimized components; run `flutter test` after each feature
   - If tests fail: inspect widget tree with Flutter DevTools, fix failing assertions, re-run `flutter test`
4. **Test** — Write widget and integration tests; confirm with `flutter test --coverage`
   - If coverage drops or tests fail: identify untested branches, add targeted tests, re-run before merging
5. **Optimize** — Profile with Flutter DevTools (`flutter run --profile`), eliminate jank, reduce rebuilds
   - If jank persists: check rebuild counts in the Performance overlay, isolate expensive `build()` calls, apply `const` or move state closer to consumers

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Riverpod | `references/riverpod-state.md` | State management, providers, notifiers |
| Bloc | `references/bloc-state.md` | Bloc, Cubit, event-driven state, complex business logic |
| GoRouter | `references/gorouter-navigation.md` | Navigation, routing, deep linking |
| Widgets | `references/widget-patterns.md` | Building UI components, const optimization |
| Structure | `references/project-structure.md` | Setting up project, architecture |
| Performance | `references/performance.md` | Optimization, profiling, jank fixes |

## Code Examples

### Riverpod Provider + ConsumerWidget (correct pattern)

```dart
// provider definition
final counterProvider = StateNotifierProvider<CounterNotifier, int>(
  (ref) => CounterNotifier(),
);

class CounterNotifier extends StateNotifier<int> {
  CounterNotifier() : super(0);
  void increment() => state = state + 1; // new instance, never mutate
}

// consuming widget — use ConsumerWidget, not StatefulWidget
class CounterView extends ConsumerWidget {
  const CounterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}
```

### Before / After — State Management

```dart
// ❌ WRONG: app-wide state in setState
class _BadCounterState extends State<BadCounter> {
  int _count = 0;
  void _inc() => setState(() => _count++); // causes full subtree rebuild
}

// ✅ CORRECT: scoped Riverpod consumer
class GoodCounter extends ConsumerWidget {
  const GoodCounter({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return IconButton(
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      icon: const Icon(Icons.add), // const on static widgets
    );
  }
}
```

## Constraints

### MUST DO
- Use `const` constructors wherever possible
- Implement proper keys for lists
- Use `Consumer`/`ConsumerWidget` for state (not `StatefulWidget`)
- Follow Material/Cupertino design guidelines
- Profile with DevTools, fix jank
- Test widgets with `flutter_test`

### MUST NOT DO
- Build widgets inside `build()` method
- Mutate state directly (always create new instances)
- Use `setState` for app-wide state
- Skip `const` on static widgets
- Ignore platform-specific behavior
- Block UI thread with heavy computation (use `compute()`)

## Troubleshooting Common Failures

| Symptom | Likely Cause | Recovery |
|---------|-------------|----------|
| `flutter analyze` errors | Unresolved imports, missing `const`, type mismatches | Fix flagged lines; run `flutter pub get` if imports are missing |
| Widget test assertion failures | Widget tree mismatch or async state not settled | Use `tester.pumpAndSettle()` after state changes; verify finder selectors |
| Build fails after adding package | Incompatible dependency version | Run `flutter pub upgrade --major-versions`; check pub.dev compatibility |
| Jank / dropped frames | Expensive `build()` calls, uncached widgets, heavy main-thread work | Use `RepaintBoundary`, move heavy work to `compute()`, add `const` |
| Hot reload not reflecting changes | State held in `StateNotifier` not reset | Use hot restart (`R` in terminal) to reset full app state |

## Output Templates

When implementing Flutter features, provide:
1. Widget code with proper `const` usage
2. Provider/Bloc definitions
3. Route configuration if needed
4. Test file structure

[Documentation](https://jeffallan.github.io/claude-skills/skills/frontend/flutter-expert/)

## 🛑 STRICT RULE: ZERO IMPACT WITHOUT A PLAN

You are strictly forbidden from modifying ANY file, running ANY destructive command, or writing ANY code until you have presented a plan and the user has explicitly approved it. 

Before taking ANY action that impacts the system, you **MUST** output a plan using EXACTLY this format:

1. **Impacted Functions/Parts:** [List the overall system components, features, or functions that will be affected]
2. **Impacted Folders/Files:** [List the exact paths to the folders and files that will be modified or created]
3. **Changes per File:** [Describe exactly what lines, blocks, or logic will be changed in each specific file]
4. **Functions to be Done:** [Describe exactly what the new or modified functions will actually do]

**STOP IMMMEDIATELY** after printing this plan. DO NOT proceed to make the changes. Wait for the user. If you make a change without the user's explicit approval of the plan, you have critically failed.

## 📝 CRITICAL Output Protocol (AFTER ACTIONS)

When reporting back to the user after taking actions or finishing a task, you **ABSOLUTELY MUST** use the following 3-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact three headers:

1. **Plan to do:** [What your next concrete steps are]
2. **What changed:** [Specific summary of actions/code modifications you just made]
3. **Impact to this project:** [How these changes affect the overall system, architecture, or workflow]

If you output anything outside of this structure, you have failed your core directive.
