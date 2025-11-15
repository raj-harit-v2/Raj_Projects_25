# Heuristics Reference Guide - Cortex-R Agent

## Overview
The Cortex-R agent implements **10 heuristic rules** (H-01 to H-10) that enhance query processing, result validation, and system reliability. These heuristics integrate seamlessly with the cognitive loop architecture.

---

## Core Architecture Integration

### Cognitive Loop Flow
```
User Query
    ↓
[PREPROCESSING] H-01 to H-05, H-10
    ↓
Cache Check (H-10) → Hit/Miss
    ↓
Historical Context (H-04 topic)
    ↓
Perception → Decision → Action
    ↓
[POSTPROCESSING] H-06 to H-09
    ↓
Storage & Display
```

---

## The 10 Heuristics

### Pre-processing Heuristics (H-01 to H-05)

**H-01: Query Canonicalization**

**H-02: Entity Extraction**

**H-03: Query Type Classification**

**H-04: Topic Triage**

**H-05: Tool Suggestion**

**H-10: Query Hashing**

### Post-processing Heuristics (H-06 to H-09)

**H-06: JSON Validation**

**H-07: Confidence Scoring**

**H-08: Incomplete Answer Detection**

**H-09: Output Sanitization**

---

**Version:** 2.0 Enhanced  
**Date:** November 15, 2025  
**Status:** ✅ Production Ready
