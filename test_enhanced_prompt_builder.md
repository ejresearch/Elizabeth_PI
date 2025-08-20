# Enhanced Prompt Builder Test Guide

## 🎯 Testing the Enhanced Brainstorming System

### What's New:

1. **Smart Bucket Insertion**
   - Click any LightRAG bucket → Modal appears
   - Configure guidance, mode, and focus level
   - Generates: `{lightrag.bucket|guidance:"..."|mode:"mix"|focus:7}`

2. **Bucket Orchestration Panel**
   - Shows configured buckets
   - Manage bucket sequences
   - Clear configurations

3. **Enhanced Template Storage**
   - Templates save bucket configurations
   - Load templates restore bucket settings
   - Bucket configuration summary

### Testing Steps:

#### 1. Start the Server
```bash
cd /Users/elle/Desktop/Elizabeth_PI
python web_brainstorm_server.py
```

#### 2. Open the Interface
- Navigate to: http://localhost:8003
- Select a project with LightRAG buckets

#### 3. Test Smart Bucket Insertion
1. Switch to "Prompt Builder" mode
2. Click any LightRAG bucket in the left panel
3. **Expected**: Modal appears with guidance configuration
4. Try preset suggestions: "Find dialogue patterns"
5. Set mode to "mix" and focus to 7
6. Click "Insert with Guidance"
7. **Expected**: Enhanced variable appears in editor

#### 4. Test Orchestration Panel
1. Add 2-3 guided buckets with different guidance
2. **Expected**: Orchestration panel appears below data blocks
3. Click "Show/Hide" to toggle orchestration view
4. **Expected**: See list of configured buckets with guidance preview

#### 5. Test Template Saving
1. Save template with configured buckets
2. Create new template and load the saved one
3. **Expected**: Bucket configurations are restored

#### 6. Test Compilation
1. Click "Preview" button
2. **Expected**: Enhanced variables compile to instructions with guidance

### Expected Enhanced Variable Format:
```
{lightrag.romcom_scripts|guidance:"Find dialogue patterns and comedic timing examples"|mode:"mix"|focus:7}
```

### Expected Compilation Output:
```
[Query romcom_scripts knowledge base with guidance: 'Find dialogue patterns and comedic timing examples' using mix mode (focus level: 7/10)]
```

## 🔧 Features Implemented:

✅ Bucket guidance modal with presets
✅ Enhanced variable format parsing
✅ Bucket orchestration panel
✅ Template storage with configurations
✅ Live configuration summary
✅ Enhanced compilation engine
✅ Smart bucket insertion workflow

## 🚀 Next Steps (Future Enhancements):

- Multi-sequence orchestration
- Bucket performance analytics
- Advanced preset library
- Integration with nell_alpha-style session runner
- Batch bucket configuration
- Bucket dependency mapping

---

The enhanced prompt builder transforms basic bucket insertion into an intelligent, guided system that matches the sophistication of the `nell_alpha` approach while maintaining the user-friendly web interface.