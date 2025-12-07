# 🚀 Quick Start - Optimized Real Estate Bot

## ⚡ FASTEST SOLUTION - Use Cached Version

The **cached version** is the most API-efficient:

```bash
streamlit run app_cached.py
```

### Why Cached Version?
- ✅ **Stores results for 1 hour** - Repeat queries use 0 API calls
- ✅ **All optimizations included** - Single agent, reduced tokens
- ✅ **Visual cache management** - See what's cached in sidebar
- ✅ **90% reduction in API calls** for repeated cities

---

## 📦 Three Versions Available

### 1. **app_cached.py** ⭐ RECOMMENDED
- All optimizations + caching
- Best for free API tier
- **Use this one!**

### 2. **app_optimized.py**
- All optimizations, no caching
- Good if you don't want caching

### 3. **app.py** (Original)
- Not optimized
- Will hit rate limits frequently

---

## 🔄 How to Switch

### Quick Test (No Changes)
```bash
streamlit run app_cached.py
```

### Permanent Switch
```bash
# Backup original
cp app.py app_backup.py

# Use cached version as main
cp app_cached.py app.py

# Run
streamlit run app.py
```

---

## 📊 Performance Comparison

| Version | API Calls | Rate Limits | Speed |
|---------|-----------|-------------|-------|
| Original | ~10-12 | Very High | Slow |
| Optimized | ~3-5 | Low | Fast |
| **Cached** | ~0-3 | **Very Low** | **Fastest** |

---

## 🎯 Usage Tips

1. **First search of a city**: Uses API (30-60 sec)
2. **Repeat search within 1 hour**: Uses cache (instant!)
3. **Clear cache**: Use sidebar button if needed
4. **Popular cities**: Cache these first to save API calls

---

## ⚙️ Configuration

In `app_cached.py`, you can adjust:

```python
CACHE_DURATION = 3600  # 1 hour (change to 7200 for 2 hours)
```

---

## 🐛 If You Still Hit Rate Limits

1. **Wait 60 seconds** between requests
2. **Use popular cities first** (they'll be cached)
3. **Clear cache** if memory issues
4. **Consider upgrading** Groq API tier

---

## 📝 Files Reference

**Core Files (Optimized):**
- `agents_optimized.py` - Single agent (reduced from 2)
- `tasks_optimized.py` - Single task (reduced from 2)
- `crew_optimized.py` - Optimized crew config
- `app_cached.py` - Streamlit app with caching ⭐

**Documentation:**
- `OPTIMIZATION_GUIDE.md` - Full optimization details
- `QUICKSTART.md` - This file

**Original Files (Backup):**
- `agents.py`, `tasks.py`, `crew.py`, `app.py`

---

## 🎉 Quick Win

Just run this command:
```bash
streamlit run app_cached.py
```

That's it! You now have:
- ✅ 60-90% fewer API calls
- ✅ Faster responses
- ✅ Rare rate limit errors
- ✅ Cached results for efficiency

---

## 💡 Pro Tips

1. **Test with same city twice** - See caching in action
2. **Check sidebar** - Monitor cached cities
3. **Popular cities** - Cache these: London, NYC, Tokyo, Berlin
4. **Clear cache** - If you want fresh data

---

## 🆘 Troubleshooting

**Still getting rate limits?**
- Increase `CACHE_DURATION` to 2 hours (7200)
- Wait 2 minutes between first-time city searches
- Use cached cities when possible

**Cache not working?**
- Ensure same city spelling
- Check sidebar for cached list
- Try clearing cache and re-running

**Want even better performance?**
- Consider using `llama-3.1-8b-instant` in `agents_optimized.py`
- Further reduce `max_tokens` to 1500

---

## 📈 Next Steps

1. **Deploy cached version** to Streamlit Cloud
2. **Monitor Groq dashboard** for API usage
3. **Share with users** - Much better experience!
4. **Consider paid tier** if scaling up

---

**Happy analyzing! 🏢💰**
