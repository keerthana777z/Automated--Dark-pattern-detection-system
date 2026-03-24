# ===============================
# Dark Pattern Preprocessing & EDA
# ===============================

library(readr)
library(dplyr)
library(stringr)
library(tidytext)
library(ggplot2)
library(textclean)
library(quanteda)
library(quanteda.textstats)

# 1. Load datasets
csv_data <- read_csv("../data/raw/dark-patterns.csv", show_col_types = FALSE)
tsv_data <- read_tsv("../data/raw/dataset.tsv", show_col_types = FALSE)

# 2. Standardize CSV columns
csv_data <- csv_data %>%
  rename(
    text  = `Pattern String`,
    label = `Pattern Category`
  ) %>%
  select(text, label)

# 3. Standardize TSV columns (CRITICAL FIX)
tsv_data <- tsv_data %>%
  select(text, `Pattern Category`) %>%   # DROP numeric label column
  rename(label = `Pattern Category`)

# 4. Merge datasets
data <- bind_rows(csv_data, tsv_data)

# 5. Remove missing values
data <- data %>% filter(!is.na(text), !is.na(label))

# 6. Text cleaning
data <- data %>%
  mutate(
    clean_text = text %>%
      tolower() %>%
      replace_html() %>%
      replace_non_ascii() %>%
      str_remove_all("[^a-z\\s]") %>%
      str_squish()
  )

# 7. Basic analytics
eda_summary <- data %>%
  group_by(label) %>%
  summarise(
    samples = n(),
    avg_length = mean(str_length(clean_text)),
    avg_words = mean(str_count(clean_text, "\\w+")),
    .groups = "drop"
  )

# 8. Readability analysis (quanteda)
corp <- corpus(data$clean_text)

read_stats <- textstat_readability(
  corp,
  measure = "Flesch.Kincaid"
)

data$readability <- read_stats$Flesch.Kincaid

readability_summary <- data %>%
  group_by(label) %>%
  summarise(
    avg_readability = mean(readability, na.rm = TRUE),
    .groups = "drop"
  )

eda_summary <- left_join(eda_summary, readability_summary, by = "label")

# 9. Save outputs
dir.create("../data/processed", showWarnings = FALSE)

write_csv(
  data %>% select(clean_text, label),
  "../data/processed/cleaned_dark_patterns.csv"
)

write_csv(
  eda_summary,
  "../data/processed/eda_summary.csv"
)

cat("✅ R preprocessing & analytics completed successfully\n")
