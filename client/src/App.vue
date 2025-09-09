<template>
  <div class="app-container">
    <header class="app-header">
      <h1>慧淘</h1>
    </header>
    <main class="app-main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
// 根组件，路由视图将在这里渲染
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #409eff;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
}
</style>